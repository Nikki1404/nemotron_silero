import asyncio
import json
import time
import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np
import torch
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from omegaconf import OmegaConf

import nemo.collections.asr as nemo_asr

# ===============================
# LOGGING SETUP
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

ASR_CHUNK_MS = 160
ASR_CHUNK_SAMPLES = int(SR * ASR_CHUNK_MS / 1000)

VAD_FRAME_SAMPLES = 512
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
# Load ASR
# ===============================
logger.info("INIT | Loading Nemotron...")
asr_model = nemo_asr.models.ASRModel.from_pretrained(
    model_name=MODEL_NAME
).to(DEVICE).eval()

logger.info(f"INIT | Model class = {asr_model.__class__.__name__}")
logger.info("INIT | Warming up model...")

with torch.no_grad():
    dummy = np.zeros(SR // 2, dtype=np.float32)
    _ = asr_model.transcribe([dummy], batch_size=1)

logger.info("INIT | Warmup complete.")

# ===============================
# Load Silero VAD
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
    PARTIAL_EVERY_S = 0.25

    try:
        while True:
            data = await ws.receive_bytes()
            logger.debug(f"AUDIO | recv_bytes={len(data)}")

            chunk = np.frombuffer(data, dtype=np.int16)

            vad_buf = np.concatenate([vad_buf, chunk])

            if vad_state.speaking:
                speech_buf = np.concatenate([speech_buf, chunk])

            end_utt = False

            # ===============================
            # VAD
            # ===============================
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
                        speech_buf = np.zeros((0,), dtype=np.int16)
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

            # ===============================
            # PARTIAL
            # ===============================
            if vad_state.speaking and (time.time() - last_partial_ts) >= PARTIAL_EVERY_S:
                last_partial_ts = time.time()

                window_s = 4.0
                max_samples = int(window_s * SR)
                use_pcm = speech_buf[-max_samples:] if len(speech_buf) > max_samples else speech_buf

                audio_f32 = use_pcm.astype(np.float32) / 32768.0

                with torch.no_grad():
                    text_list = asr_model.transcribe([audio_f32], batch_size=1)
                    text = text_list[0] if text_list else ""

                logger.debug(f"ASR | PARTIAL samples={len(use_pcm)} text='{text}'")

                if text and text != last_partial_text:
                    last_partial_text = text
                    await ws.send_text(json.dumps({"type": "partial", "text": text}))

            # ===============================
            # FINAL
            # ===============================
            if end_utt:
                audio_f32 = speech_buf.astype(np.float32) / 32768.0

                with torch.no_grad():
                    text_list = asr_model.transcribe([audio_f32], batch_size=1)
                    final_text = text_list[0] if text_list else ""

                logger.info(f"ASR | FINAL samples={len(speech_buf)} text='{final_text}'")

                await ws.send_text(json.dumps({"type": "final", "text": final_text}))

                speech_buf = np.zeros((0,), dtype=np.int16)
                last_partial_text = ""
                last_partial_ts = 0.0
                vad_state = VADState()

    except WebSocketDisconnect:
        logger.info("WS | Client disconnected")
    except Exception as e:
        logger.exception(f"WS | ERROR: {e}")
        try:
            await ws.send_text(json.dumps({"type": "error", "message": str(e)}))
        except Exception:
            pass
