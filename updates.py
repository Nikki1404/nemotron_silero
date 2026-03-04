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
import asyncio
import json
import time
import logging
import os
import numpy as np
import resampy

from fastapi import FastAPI, WebSocket
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.config import load_config, Config, MODEL_MAP
from app.metrics import *
from app.vad import AdaptiveEnergyVAD
from app.factory import build_engine
from app.asr_engines.base import ASREngine

cfg = load_config()
logging.basicConfig(level=cfg.log_level, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("asr_server")

app = FastAPI()
ENGINE_CACHE: dict[str, ASREngine] = {}

#  PRELOAD BOTH MODELS AT STARTUP (takes ~30-60s once)
async def preload_engines():
    """Preload both Whisper + Nemotron models into cache"""
    backends = ["whisper", "nemotron", "google"]
    
    log.info(" Preloading ASR engines (this happens once at startup)...")
    for backend in backends:
        try:
            model_name = MODEL_MAP[backend]
            print(f"   Loading {backend} ({model_name})...")
            
            tmp_cfg = Config()
            object.__setattr__(tmp_cfg, 'asr_backend', backend)
            object.__setattr__(tmp_cfg, 'model_name', model_name)
            object.__setattr__(tmp_cfg, 'device', cfg.device)
            object.__setattr__(tmp_cfg, 'sample_rate', cfg.sample_rate)
            object.__setattr__(tmp_cfg, 'context_right', cfg.context_right)
             
            os.environ["https_proxy"] = "http://163.116.128.80:8080"
            os.environ["http_proxy"] = "http://163.116.128.80:8080"
            
            engine = build_engine(tmp_cfg)
            load_sec = engine.load()
            
            os.environ.pop("https_proxy", None)
            os.environ.pop("http_proxy", None)
            
            log.info(f" Preloaded {backend} ({model_name}) in {load_sec:.2f}s")
            ENGINE_CACHE[backend] = engine
            
        except Exception as e:
            log.error(f" Failed to preload {backend}: {e}")
            continue
    
    log.info(" All engines preloaded! Client requests will be INSTANT.")

#  STARTUP EVENT - Preload happens automatically
@app.on_event("startup")
async def startup_event():
    await preload_engines()

def get_engine(backend: str) -> ASREngine:
    """Instant lookup from preloaded cache"""
    if backend not in ENGINE_CACHE:
        raise ValueError(f"Engine '{backend}' not preloaded. Available: {list(ENGINE_CACHE.keys())}")
    
    log.info(f" Using cached {backend} engine (0ms latency!)")
    return ENGINE_CACHE[backend]


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.websocket("/asr/realtime-custom-vad")
async def ws_asr(ws: WebSocket):
    await ws.accept()

    #  FIRST MESSAGE MUST BE CONFIG
    init = await ws.receive_text()
    init_obj = json.loads(init)

    backend = init_obj.get("backend")
    if backend not in ("nemotron", "whisper", "google"):
        await ws.close(code=4000)
        return
    
    client_sample_rate = init_obj.get("sample_rate", cfg.sample_rate)


    def upsample_if_needed(pcm: bytes) -> bytes:
        if not pcm or client_sample_rate == cfg.sample_rate:
            return pcm

        x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
        y = resampy.resample(x, client_sample_rate, cfg.sample_rate)
        y = np.clip(y, -1.0, 1.0)
        return (y * 32767.0).astype(np.int16).tobytes()


    engine = get_engine(backend)

    labels = (backend, engine.model_name)

    active_streams = ACTIVE_STREAMS.labels(*labels)
    partials_total = PARTIALS_TOTAL.labels(*labels)
    finals_total = FINALS_TOTAL.labels(*labels)
    utterances_total = UTTERANCES_TOTAL.labels(*labels)

    ttft_wall = TTFT_WALL.labels(*labels)
    ttf_wall = TTF_WALL.labels(*labels)

    infer_sec = INFER_SEC.labels(*labels)
    preproc_sec = PREPROC_SEC.labels(*labels)
    flush_sec = FLUSH_SEC.labels(*labels)

    audio_sec_hist = AUDIO_SEC.labels(*labels)
    rtf_hist = RTF.labels(*labels)
    backlog_ms_gauge = BACKLOG_MS.labels(*labels)

    active_streams.inc()
    log.info(f"WS connected ({backend}) {ws.client}")

    vad = AdaptiveEnergyVAD(
        cfg.sample_rate,
        cfg.vad_frame_ms,
        cfg.vad_start_margin,
        cfg.vad_min_noise_rms,
        cfg.pre_speech_ms,
    )

    session = engine.new_session(max_buffer_ms=cfg.max_utt_ms)

    frame_bytes = int(cfg.sample_rate * cfg.vad_frame_ms / 1000) * 2
    raw_buf = bytearray()

    utt_started = False
    utt_audio_ms = 0
    t_utt_start = None
    t_first_partial = None
    silence_ms = 0

    try:
        while True:
            msg = await ws.receive()
            if msg["type"] == "websocket.disconnect":
                break

            data = msg.get("bytes")
            if data is None:
                continue
            data = upsample_if_needed(data)

            if data == b"":
                if utt_started:
                    final = session.finalize(cfg.post_speech_pad_ms)
                    await _emit_final(
                        ws,
                        session,
                        final,
                        utt_audio_ms,
                        t_utt_start,
                        t_first_partial,
                        "eos",
                        utterances_total,
                        finals_total,
                        ttf_wall,
                        audio_sec_hist,
                        rtf_hist,
                        engine,
                    )
                break

            raw_buf.extend(data)

            while len(raw_buf) >= frame_bytes:
                frame = bytes(raw_buf[:frame_bytes])
                del raw_buf[:frame_bytes]

                is_speech, pre = vad.push_frame(frame)
                silence_ms = 0 if is_speech else silence_ms + cfg.vad_frame_ms

                if pre and not utt_started:
                    utt_started = True
                    utt_audio_ms = 0
                    t_utt_start = time.time()
                    t_first_partial = None
                    silence_ms = 0
                    session.accept_pcm16(pre)

                if not utt_started:
                    continue

                session.accept_pcm16(frame)
                utt_audio_ms += cfg.vad_frame_ms

                if engine.caps.partials:
                    text = session.step_if_ready()
                    if text:
                        partials_total.inc()
                        if t_first_partial is None:
                            t_first_partial = time.time()
                            if engine.caps.ttft_meaningful:
                                ttft_wall.observe(t_first_partial - t_utt_start)

                        log.info(f"CLIENT: {ws.client}, TEXT: {text}, START_TIME : {int(t_utt_start * 1000)}")
                        await ws.send_text(json.dumps({
                            "type": "partial", 
                            "text": text,
                            "t_start": int(t_utt_start * 1000)
                        }))

                if (
                    not is_speech
                    and utt_audio_ms >= cfg.min_utt_ms
                    and silence_ms >= cfg.end_silence_ms
                ):
                    final = session.finalize(cfg.post_speech_pad_ms)
                    await _emit_final(
                        ws,
                        session,
                        final,
                        utt_audio_ms,
                        t_utt_start,
                        t_first_partial,
                        "silence",
                        utterances_total,
                        finals_total,
                        ttf_wall,
                        audio_sec_hist,
                        rtf_hist,
                        engine,
                    )
                    vad.reset()
                    utt_started = False
                    utt_audio_ms = 0
                    silence_ms = 0

    finally:
        active_streams.dec()
        await ws.close()
        log.info("WS disconnected")


async def _emit_final(
    ws,
    session,
    final_text,
    audio_ms,
    t_start,
    t_first_partial,
    reason,
    utterances_total,
    finals_total,
    ttf_wall,
    audio_sec_hist,
    rtf_hist,
    engine,
):
    if not final_text:
        return

    utterances_total.inc()
    finals_total.inc()

    audio_sec = audio_ms / 1000.0
    ttf = time.time() - t_start

    ttf_wall.observe(ttf)
    audio_sec_hist.observe(audio_sec)

    compute_sec = session.utt_preproc + session.utt_infer + session.utt_flush
    if audio_sec > 0:
        rtf_hist.observe(compute_sec / audio_sec)

    log.info(f"CLIENT: {ws.client}, TEXT: {final_text}")

    await ws.send_text(json.dumps({
        "type": "final",
        "text": final_text,
        "reason": reason,
        "t_start": int(t_start * 1000),
        "audio_ms": audio_ms,
        "ttf_ms": int(ttf * 1000),
        "ttft_ms": (
            int((t_first_partial - t_start) * 1000)
            if t_first_partial and engine.caps.ttft_meaningful
            else None
        ),
        "chunks": session.chunks,
        "model_preproc_ms": int(session.utt_preproc * 1000),
        "model_infer_ms": int(session.utt_infer * 1000),
        "model_flush_ms": int(session.utt_flush * 1000),
        "rtf": (compute_sec / audio_sec) if audio_sec > 0 else None,
    }))
