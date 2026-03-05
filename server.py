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
# (Recommended for better latency/stability vs 6s @ 0.35s, but keep if you want)
PARTIAL_EVERY_S = 0.60
PARTIAL_WINDOW_S = 4.0

# VAD
VAD_FRAME_SAMPLES = 512     # 32ms @ 16k
VAD_START_TH = 0.45         # speech start threshold (after smoothing)
VAD_END_TH = 0.25           # speech end threshold (after smoothing)
MIN_SILENCE_MS = 800        # slightly less aggressive endpointing for read speech
MAX_UTT_S = 20.0

# Safety: Nemotron often needs enough speech audio to output text
MIN_UTT_AUDIO_MS_FOR_ASR = 700  # reduce empty/blank outputs

# Padding to avoid missing first/last words (big WER win vs Silero default)
PRE_ROLL_MS = 250
POST_ROLL_MS = 350
PRE_ROLL_SAMPLES = int(SR * PRE_ROLL_MS / 1000)
POST_ROLL_SAMPLES = int(SR * POST_ROLL_MS / 1000)

# Smooth Silero probability to reduce chattering / early end
EMA_ALPHA = 0.90  # higher = smoother (0.85-0.95 typical)

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

    # New buffers for improved Silero integration
    pre_roll_buf = np.zeros((0,), dtype=np.int16)
    post_roll_remaining = 0
    p_smooth = 0.0

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

            # Maintain rolling pre-roll buffer always (big WER win)
            pre_roll_buf = np.concatenate([pre_roll_buf, chunk])
            if pre_roll_buf.size > PRE_ROLL_SAMPLES:
                pre_roll_buf = pre_roll_buf[-PRE_ROLL_SAMPLES:]

            # periodic audio-level log (confirms mic is not silent)
            now = time.time()
            if now - last_audio_log_ts >= 1.0:
                last_audio_log_ts = now
                logger.debug(
                    f"AUDIO | recv_bytes={len(data)} rms_db={pcm16_rms_db(chunk):.1f}dB (client_sr={client_sample_rate})"
                )

            # Always append to VAD buffer
            vad_buf = np.concatenate([vad_buf, chunk])

            # Collect speech when in speaking OR during post-roll
            if vad_state.speaking:
                speech_buf = np.concatenate([speech_buf, chunk])
            elif post_roll_remaining > 0:
                take = min(post_roll_remaining, chunk.size)
                if take > 0:
                    speech_buf = np.concatenate([speech_buf, chunk[:take]])
                    post_roll_remaining -= take
                if post_roll_remaining <= 0:
                    logger.info("VAD | POST_ROLL complete -> FINALIZE")
                    end_utt = True
                else:
                    end_utt = False
            else:
                end_utt = False

            # ---- VAD ----
            while len(vad_buf) >= VAD_FRAME_SAMPLES:
                frame = vad_buf[:VAD_FRAME_SAMPLES]
                vad_buf = vad_buf[VAD_FRAME_SAMPLES:]

                p_raw = silero_prob_32ms(frame)
                # EMA smoothing
                p_smooth = EMA_ALPHA * p_smooth + (1.0 - EMA_ALPHA) * p_raw
                p = p_smooth

                frame_ms = int(1000 * (VAD_FRAME_SAMPLES / SR))
                tnow = time.time()

                logger.debug(f"VAD | p={p:.3f} (raw={p_raw:.3f}) speaking={vad_state.speaking} post_roll={post_roll_remaining}")

                if not vad_state.speaking and post_roll_remaining <= 0:
                    if p >= VAD_START_TH:
                        vad_state.speaking = True
                        vad_state.silence_ms = 0
                        vad_state.utt_start_t = tnow

                        # Prepend pre-roll so we don't miss first words
                        speech_buf = pre_roll_buf.copy()

                        last_partial_text = ""
                        last_partial_ts = 0.0
                        logger.info("VAD | SPEECH_START (with pre-roll)")
                elif vad_state.speaking:
                    if p <= VAD_END_TH:
                        vad_state.silence_ms += frame_ms
                        if vad_state.silence_ms >= MIN_SILENCE_MS:
                            # Stop speaking, begin post-roll instead of immediate finalize
                            vad_state.speaking = False
                            post_roll_remaining = POST_ROLL_SAMPLES
                            logger.info("VAD | SPEECH_END (post-roll started)")
                    else:
                        vad_state.silence_ms = 0

                    if vad_state.utt_start_t and (tnow - vad_state.utt_start_t) >= MAX_UTT_S:
                        vad_state.speaking = False
                        post_roll_remaining = 0
                        end_utt = True
                        logger.info("VAD | MAX_UTT_END -> FINALIZE")

            # ---- PARTIAL ----
            if (
                vad_state.speaking
                and speech_buf.size > 0
                and (time.time() - last_partial_ts) >= PARTIAL_EVERY_S
            ):
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
                post_roll_remaining = 0
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
