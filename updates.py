#server.py(nemotron_silero)
import json
import time
import logging
from dataclasses import dataclass
from typing import Optional, Any

import numpy as np
import torch
import resampy
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

import nemo.collections.asr as nemo_asr

# ===============================
# LOGGING
# ===============================
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-5s | %(name)s | %(message)s",
)
logger = logging.getLogger("ASR_SERVER")

# ===============================
# CONFIG
# ===============================
SR = 16000

# Partial behavior (sliding window)
PARTIAL_EVERY_S = 0.35      # how often to emit partials (increase if GPU is weak)
PARTIAL_WINDOW_S = 6.0      # longer window helps Nemotron produce text reliably

# VAD
VAD_FRAME_SAMPLES = 512     # 32ms @ 16k
VAD_START_TH = 0.45         # 🔥 lowered (more sensitive)
VAD_END_TH = 0.25           # 🔥 lowered
MIN_SILENCE_MS = 600        # 🔥 more tolerant, avoids early cutoffs
MAX_UTT_S = 20.0

# Safety: Nemotron often needs enough speech audio to output text
MIN_UTT_AUDIO_MS_FOR_ASR = 400  # don’t call ASR if speech < 400ms (prevents empty outputs)

MODEL_NAME = "nvidia/nemotron-speech-streaming-en-0.6b"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

app = FastAPI()


@app.get("/health")
def health():
    return {"ok": True, "device": DEVICE, "model": MODEL_NAME, "sr": SR}


# ===============================
# NeMo output -> plain string
# ===============================
def nemo_to_text(x: Any) -> str:
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    if hasattr(x, "text"):
        try:
            return x.text or ""
        except Exception:
            return ""
    if isinstance(x, (list, tuple)):
        if len(x) == 0:
            return ""
        return nemo_to_text(x[0])
    return str(x)


def transcribe_text(audio_f32: np.ndarray) -> str:
    """Always returns a string, never Hypothesis."""
    if audio_f32.size == 0:
        return ""
    with torch.no_grad():
        out = asr_model.transcribe([audio_f32], batch_size=1)
    return nemo_to_text(out).strip()


def pcm16_rms_db(pcm16: np.ndarray) -> float:
    if pcm16.size == 0:
        return -120.0
    x = pcm16.astype(np.float32) / 32768.0
    rms = float(np.sqrt(np.mean(x * x) + 1e-12))
    db = 20.0 * np.log10(rms + 1e-12)
    return db


def upsample_if_needed(pcm: bytes, client_sample_rate: int) -> bytes:
    """
    Resample client audio to server SR (16k) if needed.
    """
    if not pcm or client_sample_rate == SR:
        return pcm

    x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
    y = resampy.resample(x, client_sample_rate, SR)
    y = np.clip(y, -1.0, 1.0)
    return (y * 32767.0).astype(np.int16).tobytes()


# ===============================
# Load ASR
# ===============================
logger.info("INIT | Loading Nemotron...")
asr_model = nemo_asr.models.ASRModel.from_pretrained(model_name=MODEL_NAME).to(DEVICE).eval()
logger.info(f"INIT | Model class: {asr_model.__class__.__name__} | DEVICE={DEVICE}")

logger.info("INIT | Warming up...")
dummy = np.zeros(SR, dtype=np.float32)  # 1s
warm = transcribe_text(dummy)
logger.info(f"INIT | Warmup done. (warmup_text='{warm}')")

# ===============================
# Load Silero VAD (CPU)
# ===============================
logger.info("INIT | Loading Silero VAD...")
vad_model, _ = torch.hub.load("snakers4/silero-vad", "silero_vad", trust_repo=True)
vad_model.to("cpu").eval()
logger.info("INIT | Silero ready.")


def silero_prob_32ms(frame_pcm16: np.ndarray) -> float:
    audio = frame_pcm16.astype(np.float32) / 32768.0
    with torch.no_grad():
        return float(vad_model(torch.from_numpy(audio), SR).item())


@dataclass
class VADState:
    speaking: bool = False
    silence_ms: int = 0
    utt_start_t: Optional[float] = None


@app.websocket("/ws")
async def ws_asr(ws: WebSocket):
    await ws.accept()
    logger.info("WS | Client connected")

    vad_state = VADState()
    vad_buf = np.zeros((0,), dtype=np.int16)
    speech_buf = np.zeros((0,), dtype=np.int16)

    last_partial_text = ""
    last_partial_ts = 0.0
    last_audio_log_ts = 0.0

    # default client rate unless client sends config
    client_sample_rate = SR

    try:
        while True:
            msg = await ws.receive()

            if "bytes" in msg and msg["bytes"] is not None:
                data = msg["bytes"]
            elif "text" in msg and msg["text"] is not None:
                # Allow a config message from client: {"type":"config","sample_rate":48000}
                try:
                    meta = json.loads(msg["text"])
                    if isinstance(meta, dict) and meta.get("type") == "config":
                        client_sample_rate = int(meta.get("sample_rate", SR))
                        logger.info(f"WS | Client sample_rate set to {client_sample_rate}")
                    continue
                except Exception:
                    continue
            else:
                continue

            # upsample if needed
            data = upsample_if_needed(data, client_sample_rate)

            chunk = np.frombuffer(data, dtype=np.int16)
            vad_buf = np.concatenate([vad_buf, chunk])

            # periodic audio-level log (confirms mic is not silent)
            now = time.time()
            if now - last_audio_log_ts >= 1.0:
                last_audio_log_ts = now
                logger.debug(f"AUDIO | recv_bytes={len(data)} rms_db={pcm16_rms_db(chunk):.1f}dB (client_sr={client_sample_rate})")

            # only collect speech after VAD start
            if vad_state.speaking:
                speech_buf = np.concatenate([speech_buf, chunk])

            end_utt = False

            # ---- VAD ----
            while len(vad_buf) >= VAD_FRAME_SAMPLES:
                frame = vad_buf[:VAD_FRAME_SAMPLES]
                vad_buf = vad_buf[VAD_FRAME_SAMPLES:]

                p = silero_prob_32ms(frame)
                frame_ms = int(1000 * (VAD_FRAME_SAMPLES / SR))
                tnow = time.time()

                logger.debug(f"VAD | p={p:.3f} speaking={vad_state.speaking}")

                if not vad_state.speaking:
                    if p >= VAD_START_TH:
                        vad_state.speaking = True
                        vad_state.silence_ms = 0
                        vad_state.utt_start_t = tnow
                        speech_buf = np.zeros((0,), dtype=np.int16)
                        last_partial_text = ""
                        last_partial_ts = 0.0
                        logger.info("VAD | SPEECH_START")
                else:
                    if p <= VAD_END_TH:
                        vad_state.silence_ms += frame_ms
                        if vad_state.silence_ms >= MIN_SILENCE_MS:
                            vad_state.speaking = False
                            end_utt = True
                            logger.info("VAD | SPEECH_END")
                    else:
                        vad_state.silence_ms = 0

                    if vad_state.utt_start_t and (tnow - vad_state.utt_start_t) >= MAX_UTT_S:
                        vad_state.speaking = False
                        end_utt = True
                        logger.info("VAD | MAX_UTT_END")

            # ---- PARTIAL ----
            if vad_state.speaking and speech_buf.size > 0 and (time.time() - last_partial_ts) >= PARTIAL_EVERY_S:
                last_partial_ts = time.time()

                utt_ms = int(1000 * (speech_buf.size / SR))
                if utt_ms < MIN_UTT_AUDIO_MS_FOR_ASR:
                    logger.debug(f"ASR | PARTIAL skip (utt_ms={utt_ms} < {MIN_UTT_AUDIO_MS_FOR_ASR})")
                else:
                    max_samples = int(PARTIAL_WINDOW_S * SR)
                    use_pcm = speech_buf[-max_samples:] if speech_buf.size > max_samples else speech_buf
                    audio_f32 = use_pcm.astype(np.float32) / 32768.0

                    text = transcribe_text(audio_f32)
                    logger.debug(f"ASR | PARTIAL window_ms={int(1000*use_pcm.size/SR)} text='{text}'")

                    if text and text != last_partial_text:
                        last_partial_text = text
                        await ws.send_text(json.dumps({"type": "partial", "text": text}))

            # ---- FINAL ----
            if end_utt:
                utt_ms = int(1000 * (speech_buf.size / SR))
                if utt_ms < MIN_UTT_AUDIO_MS_FOR_ASR:
                    final_text = ""
                    logger.info(f"ASR | FINAL skipped (utt_ms={utt_ms} too short)")
                else:
                    audio_f32 = speech_buf.astype(np.float32) / 32768.0
                    final_text = transcribe_text(audio_f32)
                    logger.info(f"ASR | FINAL utt_ms={utt_ms} text='{final_text}'")

                await ws.send_text(json.dumps({"type": "final", "text": final_text}))

                # reset
                speech_buf = np.zeros((0,), dtype=np.int16)
                vad_state = VADState()
                last_partial_text = ""
                last_partial_ts = 0.0

    except WebSocketDisconnect:
        logger.info("WS | Client disconnected")
    except Exception as e:
        logger.exception(f"WS | ERROR: {e}")
        try:
            await ws.send_text(json.dumps({"type": "error", "message": str(e)}))
        except Exception:
            pass
          

#server.py(nemotron_custom_vad)
import json
import time
import logging
from typing import Optional
import os
import wave
import uuid

# ADDED
import numpy as np
import resampy

from fastapi import FastAPI, WebSocket
from fastapi.responses import Response
from fastapi.websockets import WebSocketDisconnect
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.config import load_config
from app.metrics import *
from app.vad import AdaptiveEnergyVAD
from app.nemotron_streaming import NemotronStreamingASR

cfg = load_config()
logging.basicConfig(level=cfg.log_level)
log = logging.getLogger("asr_server")

app = FastAPI()
engine: Optional[NemotronStreamingASR] = None


@app.on_event("startup")
async def startup():
    global engine
    engine = NemotronStreamingASR(
        model_name=cfg.model_name,
        device=cfg.device,
        sample_rate=cfg.sample_rate,
        context_right=cfg.context_right,
    )
    load_sec = engine.load()
    log.info(f"Loaded model={cfg.model_name} in {load_sec:.2f}s on {cfg.device}")


@app.get("/health")
async def health():
    return {"ok": True}


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.websocket("/ws/asr")
async def ws_asr(ws: WebSocket):
    assert engine is not None

    session_id = uuid.uuid4().hex[:8]

    ws_open = False

    # ADDED: per-connection sample rate (default = 16k)
    client_sample_rate = cfg.sample_rate

    try:
        await ws.accept()
        ws_open = True
    except Exception as e:
        log.error(f"WS accept failed: {e}")
        return

    ACTIVE_STREAMS.inc()
    log.info(f"WS connected: {ws.client} session={session_id}")

    vad = AdaptiveEnergyVAD(
        cfg.sample_rate,
        cfg.vad_frame_ms,
        cfg.vad_start_margin,
        cfg.vad_min_noise_rms,
        cfg.pre_speech_ms,
    )

    session = engine.new_session(max_buffer_ms=cfg.max_buffer_ms)

    utt_started = False
    utt_audio_ms = 0
    t_start = None
    t_first_partial = None
    silence_ms = 0

    frame_bytes = int(cfg.sample_rate * (cfg.vad_frame_ms / 1000.0) * 2)
    pcm_buffer = bytearray()
    received_pcm = bytearray()

    def reset_utt_state():
        nonlocal utt_started, utt_audio_ms, t_start, t_first_partial, silence_ms
        vad.reset()
        utt_started = False
        utt_audio_ms = 0
        t_start = None
        t_first_partial = None
        silence_ms = 0

    async def safe_send_text(payload: str) -> bool:
        nonlocal ws_open
        if not ws_open:
            return False
        try:
            await ws.send_text(payload)
            return True
        except (WebSocketDisconnect, RuntimeError) as e:
            ws_open = False
            log.warning(f"WS send failed (closed): {e}")
            return False
        except Exception as e:
            ws_open = False
            log.warning(f"WS send failed (unknown): {e}")
            return False

    def dump_received_audio():
        if not received_pcm:
            return

        debug_dir = getattr(cfg, "debug_audio_dir", "./debug_audio")
        os.makedirs(debug_dir, exist_ok=True)

        wav_path = os.path.join(
            debug_dir,
            f"ws_{session_id}_{int(time.time() * 1000)}.wav"
        )

        with wave.open(wav_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(cfg.sample_rate)
            wf.writeframes(received_pcm)

        log.info(f"[ASR][DEBUG][{session_id}] WAV dumped → {wav_path}")
        received_pcm.clear()

    # ADDED: upsample helper (only used if client is 8k)
    def upsample_if_needed(pcm: bytes) -> bytes:
        if not pcm or client_sample_rate == cfg.sample_rate:
            return pcm

        x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
        y = resampy.resample(x, client_sample_rate, cfg.sample_rate)
        y = np.clip(y, -1.0, 1.0)
        return (y * 32767.0).astype(np.int16).tobytes()

    async def finalize_and_emit(reason: str):
        nonlocal utt_started, utt_audio_ms, t_start, t_first_partial, silence_ms

        if not utt_started:
            return

        snap_chunks = int(getattr(session, "chunks", 0))
        snap_preproc = float(getattr(session, "utt_preproc", 0.0))
        snap_infer = float(getattr(session, "utt_infer", 0.0))

        flush_t0 = time.perf_counter()
        final = session.finalize(cfg.finalize_pad_ms).strip()
        flush_wall = time.perf_counter() - flush_t0

        dump_received_audio()

        UTTERANCES_TOTAL.inc()
        FINALS_TOTAL.inc()

        now = time.time()
        ttf_sec = (now - t_start) if t_start else 0.0
        TTF_WALL.observe(ttf_sec)

        if t_first_partial and t_start:
            TTFT_WALL.observe(t_first_partial - t_start)

        audio_sec = utt_audio_ms / 1000.0
        AUDIO_SEC.observe(audio_sec)

        PREPROC_SEC.observe(snap_preproc)
        INFER_SEC.observe(snap_infer)
        FLUSH_SEC.observe(flush_wall)

        rtf = None
        if audio_sec > 0:
            rtf = snap_infer / audio_sec
            RTF.observe(rtf)

        payload = {
            "type": "final",
            "text": final,
            "reason": reason,
            "audio_ms": utt_audio_ms,
            "ttft_ms": int((t_first_partial - t_start) * 1000) if (t_first_partial and t_start) else None,
            "ttf_ms": int(ttf_sec * 1000),
            "rtf": rtf,
            "chunks": snap_chunks,
            "preproc_ms": int(snap_preproc * 1000),
            "infer_ms": int(snap_infer * 1000),
            "flush_ms": int(flush_wall * 1000),
        }

        log.info(
            f"[ASR][FINAL][{session_id}] reason={reason} audio_ms={utt_audio_ms} "
            f"text='{final}'"
        )

        await safe_send_text(json.dumps(payload))
        reset_utt_state()

    try:
        while True:
            try:
                msg = await ws.receive()
            except WebSocketDisconnect:
                ws_open = False
                await finalize_and_emit("disconnect")
                break
            except Exception as e:
                log.error(f"WS receive failed: {e}")
                ws_open = False
                await finalize_and_emit("receive_error")
                break

            # ADDED: handshake parser
            if msg.get("text"):
                try:
                    meta = json.loads(msg["text"])
                    if meta.get("type") == "start" and "sample_rate" in meta:
                        client_sample_rate = int(meta["sample_rate"])
                        log.info(
                            f"[ASR][{session_id}] Client sample rate set to {client_sample_rate}Hz"
                        )
                        continue
                except Exception:
                    pass

            pcm = msg.get("bytes")

            if pcm is None:
                continue

            pcm = upsample_if_needed(pcm)

            if pcm:
                received_pcm.extend(pcm)

            if pcm == b"":
                ws_open = False
                await finalize_and_emit("eos")
                break

            pcm_buffer.extend(pcm)

            while len(pcm_buffer) >= frame_bytes:
                frame = bytes(pcm_buffer[:frame_bytes])
                del pcm_buffer[:frame_bytes]

                is_speech, pre = vad.push_frame(frame)

                if is_speech:
                    silence_ms = 0
                else:
                    silence_ms += cfg.vad_frame_ms

                if pre and not utt_started:
                    utt_started = True
                    utt_audio_ms = 0
                    t_start = time.time()
                    t_first_partial = None
                    session.accept_pcm16(pre)

                if not utt_started:
                    continue

                session.accept_pcm16(frame)
                utt_audio_ms += cfg.vad_frame_ms

                text = session.step_if_ready()
                if text:
                    if t_first_partial is None:
                        t_first_partial = time.time()

                    PARTIALS_TOTAL.inc()
                    log.debug(f"[ASR][PARTIAL][{session_id}] {text}")

                    ok = await safe_send_text(json.dumps({"type": "partial", "text": text}))
                    if not ok:
                        ws_open = False
                        break

                should_finalize = (
                    silence_ms >= cfg.end_silence_ms
                    and utt_audio_ms >= cfg.min_utt_ms
                )

                if utt_audio_ms >= cfg.max_utt_ms:
                    should_finalize = True

                if should_finalize:
                    reason = "pause" if silence_ms >= cfg.end_silence_ms else "max_utt"
                    await finalize_and_emit(reason)

            if not ws_open:
                break

    finally:
        ACTIVE_STREAMS.dec()
        if ws_open:
            try:
                await ws.close()
            except Exception:
                pass
        log.info(f"WS disconnected session={session_id}")
