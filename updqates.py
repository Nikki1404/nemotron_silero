import asyncio
import json
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np
import torch
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

import nemo.collections.asr as nemo_asr

# ===============================
# DEBUG FLAGS
# ===============================
DEBUG_AUDIO = True
DEBUG_VAD = True
DEBUG_ASR = True

# ===============================
# CONFIG
# ===============================
SR = 16000
ASR_CHUNK_MS = 160
ASR_CHUNK_SAMPLES = int(SR * ASR_CHUNK_MS / 1000)

VAD_FRAME_SAMPLES = 512
VAD_START_TH = 0.6
VAD_END_TH = 0.35
MIN_SILENCE_MS = 400

MODEL_NAME = "nvidia/nemotron-speech-streaming-en-0.6b"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

app = FastAPI()


@app.get("/health")
def health():
    return {"ok": True, "device": DEVICE}


# ===============================
# Load Nemotron (Built-In Streaming)
# ===============================
print("[INIT] Loading Nemotron...")
asr_model = nemo_asr.models.ASRModel.from_pretrained(
    model_name=MODEL_NAME
).to(DEVICE).eval()

print("[INIT] Nemotron ready.")


# ===============================
# Load Silero VAD
# ===============================
print("[INIT] Loading Silero VAD...")
vad_model, _ = torch.hub.load("snakers4/silero-vad", "silero_vad", trust_repo=True)
vad_model.to("cpu").eval()


def silero_prob(frame):
    audio = frame.astype(np.float32) / 32768.0
    with torch.no_grad():
        return float(vad_model(torch.from_numpy(audio), SR).item())


@dataclass
class VADState:
    speaking: bool = False
    silence_ms: int = 0


# ===============================
# WebSocket
# ===============================
@app.websocket("/ws")
async def ws_asr(ws: WebSocket):
    await ws.accept()

    vad_state = VADState()
    vad_buf = np.zeros((0,), dtype=np.int16)
    asr_buf = np.zeros((0,), dtype=np.int16)

    try:
        while True:
            data = await ws.receive_bytes()

            if DEBUG_AUDIO:
                print(f"[AUDIO] {len(data)} bytes")

            chunk = np.frombuffer(data, dtype=np.int16)

            vad_buf = np.concatenate([vad_buf, chunk])
            asr_buf = np.concatenate([asr_buf, chunk])

            end_utt = False

            # ===============================
            # VAD PROCESS
            # ===============================
            while len(vad_buf) >= VAD_FRAME_SAMPLES:
                frame = vad_buf[:VAD_FRAME_SAMPLES]
                vad_buf = vad_buf[VAD_FRAME_SAMPLES:]

                p = silero_prob(frame)

                if DEBUG_VAD:
                    print(f"[VAD] prob={p:.3f}")

                if not vad_state.speaking:
                    if p >= VAD_START_TH:
                        vad_state.speaking = True
                        print("[VAD] SPEECH START")
                else:
                    if p <= VAD_END_TH:
                        vad_state.speaking = False
                        end_utt = True
                        print("[VAD] SPEECH END")

            # ===============================
            # ASR PROCESS (Built-In Streaming)
            # ===============================
            if vad_state.speaking:
                while len(asr_buf) >= ASR_CHUNK_SAMPLES:
                    chunk = asr_buf[:ASR_CHUNK_SAMPLES]
                    asr_buf = asr_buf[ASR_CHUNK_SAMPLES:]

                    audio_f32 = chunk.astype(np.float32) / 32768.0

                    with torch.no_grad():
                        result = asr_model.streaming_transcribe(
                            audio=[audio_f32],
                            sample_rate=SR,
                        )

                    text = result[0] if result else ""

                    if DEBUG_ASR:
                        print(f"[ASR] TEXT: '{text}'")

                    if text:
                        await ws.send_text(
                            json.dumps({"type": "partial", "text": text})
                        )

            if end_utt:
                print("[FINAL]")
                await ws.send_text(
                    json.dumps({"type": "final", "text": ""})
                )
                asr_buf = np.zeros((0,), dtype=np.int16)

    except WebSocketDisconnect:
        print("Client disconnected")
