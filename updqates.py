import json
import time
import logging
from dataclasses import dataclass
from typing import Optional, Any

import numpy as np
import torch
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

# We still receive audio continuously; partials are produced by re-transcribing a sliding window.
PARTIAL_EVERY_S = 0.25     # how often to emit partials
PARTIAL_WINDOW_S = 4.0     # sliding window length for partial decoding

VAD_FRAME_SAMPLES = 512    # 32ms @ 16k
VAD_START_TH = 0.60
VAD_END_TH = 0.35
MIN_SILENCE_MS = 400
MAX_UTT_S = 20.0

MODEL_NAME = "nvidia/nemotron-speech-streaming-en-0.6b"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

app = FastAPI()


@app.get("/health")
def health():
    return {"ok": True, "device": DEVICE, "model": MODEL_NAME, "sr": SR}


# ===============================
# Safe conversion: NeMo output -> text
# ===============================
def nemo_to_text(x: Any) -> str:
    """
    NeMo RNNT often returns Hypothesis objects. Sometimes transcribe returns:
      - list[str]
      - list[Hypothesis]
      - list[list[Hypothesis]]
      - Hypothesis
    This function ALWAYS returns a plain string.
    """
    if x is None:
        return ""

    # already text
    if isinstance(x, str):
        return x

    # hypothesis-like object
    if hasattr(x, "text"):
        try:
            return x.text or ""
        except Exception:
            return ""

    # list/tuple: pick first element recursively
    if isinstance(x, (list, tuple)):
        if len(x) == 0:
            return ""
        return nemo_to_text(x[0])

    # fallback
    return str(x)


def transcribe_text(audio_f32: np.ndarray) -> str:
    """
    Always returns string, never Hypothesis.
    """
    if audio_f32.size == 0:
        return ""
    with torch.no_grad():
        out = asr_model.transcribe([audio_f32], batch_size=1)
    return nemo_to_text(out)


# ===============================
# Load ASR
# ===============================
logger.info("INIT | Loading Nemotron...")
asr_model = nemo_asr.models.ASRModel.from_pretrained(model_name=MODEL_NAME).to(DEVICE).eval()
logger.info(f"INIT | Model class: {asr_model.__class__.__name__}")

logger.info("INIT | Warming up...")
dummy = np.zeros(SR // 2, dtype=np.float32)
_ = transcribe_text(dummy)
logger.info("INIT | Warmup done.")

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


# ===============================
# WebSocket
# ===============================
@app.websocket("/ws")
async def ws_asr(ws: WebSocket):
    await ws.accept()
    logger.info("WS | Client connected")

    vad_state = VADState()
    vad_buf = np.zeros((0,), dtype=np.int16)
    speech_buf = np.zeros((0,), dtype=np.int16)

    last_partial_text = ""
    last_partial_ts = 0.0

    try:
        while True:
            data = await ws.receive_bytes()
            logger.debug(f"AUDIO | recv_bytes={len(data)}")

            chunk = np.frombuffer(data, dtype=np.int16)
            vad_buf = np.concatenate([vad_buf, chunk])

            # Only accumulate into speech buffer after speech starts
            if vad_state.speaking:
                speech_buf = np.concatenate([speech_buf, chunk])

            end_utt = False

            # ---------------------------
            # VAD loop
            # ---------------------------
            while len(vad_buf) >= VAD_FRAME_SAMPLES:
                frame = vad_buf[:VAD_FRAME_SAMPLES]
                vad_buf = vad_buf[VAD_FRAME_SAMPLES:]

                p = silero_prob_32ms(frame)
                frame_ms = int(1000 * (VAD_FRAME_SAMPLES / SR))
                now = time.time()

                logger.debug(f"VAD | p={p:.3f} speaking={vad_state.speaking}")

                if not vad_state.speaking:
                    if p >= VAD_START_TH:
                        vad_state.speaking = True
                        vad_state.silence_ms = 0
                        vad_state.utt_start_t = now
                        speech_buf = np.zeros((0,), dtype=np.int16)  # reset at start
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

                    if vad_state.utt_start_t and (now - vad_state.utt_start_t) >= MAX_UTT_S:
                        vad_state.speaking = False
                        end_utt = True
                        logger.info("VAD | MAX_UTT_END")

            # ---------------------------
            # PARTIAL (while speaking)
            # ---------------------------
            if vad_state.speaking and speech_buf.size > 0 and (time.time() - last_partial_ts) >= PARTIAL_EVERY_S:
                last_partial_ts = time.time()

                max_samples = int(PARTIAL_WINDOW_S * SR)
                use_pcm = speech_buf[-max_samples:] if speech_buf.size > max_samples else speech_buf
                audio_f32 = use_pcm.astype(np.float32) / 32768.0

                text = transcribe_text(audio_f32)

                logger.debug(f"ASR | PARTIAL samples={use_pcm.size} text='{text}'")

                # Never send empty/duplicate partials
                if text and text != last_partial_text:
                    last_partial_text = text
                    await ws.send_text(json.dumps({"type": "partial", "text": text}))

            # ---------------------------
            # FINAL (end of utterance)
            # ---------------------------
            if end_utt:
                audio_f32 = speech_buf.astype(np.float32) / 32768.0
                final_text = transcribe_text(audio_f32)

                logger.info(f"ASR | FINAL samples={speech_buf.size} text='{final_text}'")

                await ws.send_text(json.dumps({"type": "final", "text": final_text}))

                # reset utterance buffers/state
                speech_buf = np.zeros((0,), dtype=np.int16)
                vad_state = VADState()
                last_partial_text = ""
                last_partial_ts = 0.0

    except WebSocketDisconnect:
        logger.info("WS | Client disconnected")
    except Exception as e:
        logger.exception(f"WS | ERROR: {e}")
        # Try to return an error message; if this fails, just close.
        try:
            await ws.send_text(json.dumps({"type": "error", "message": str(e)}))
        except Exception:
            pass
