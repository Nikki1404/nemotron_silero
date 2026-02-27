import asyncio
import json
import time
import copy
from dataclasses import dataclass
from typing import Optional

import numpy as np
import torch
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from omegaconf import OmegaConf, open_dict

import nemo.collections.asr as nemo_asr
from nemo.collections.asr.models.ctc_bpe_models import EncDecCTCModelBPE
from nemo.collections.asr.parts.utils.rnnt_utils import Hypothesis

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

ASR_CHUNK_MS = 160   # 🔥 increased for stability
ASR_CHUNK_SAMPLES = int(SR * ASR_CHUNK_MS / 1000)

VAD_FRAME_SAMPLES = 512  # 32ms

VAD_START_TH = 0.60
VAD_END_TH = 0.35
MIN_SPEECH_MS = 120
MIN_SILENCE_MS = 400   # 🔥 slightly higher to avoid early cut
MAX_UTT_S = 20.0

MODEL_NAME = "nvidia/nemotron-speech-streaming-en-0.6b"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

app = FastAPI()


@app.get("/health")
def health():
    return {"ok": True, "device": DEVICE}


# ===============================
# Helpers
# ===============================

def extract_transcriptions(hyps):
    if not hyps:
        return [""]
    if isinstance(hyps[0], Hypothesis):
        return [h.text for h in hyps]
    return hyps


def init_streaming_preprocessor(asr_model):
    cfg = copy.deepcopy(asr_model._cfg)
    OmegaConf.set_struct(cfg.preprocessor, False)
    cfg.preprocessor.dither = 0.0
    cfg.preprocessor.pad_to = 0
    cfg.preprocessor.normalize = "None"

    pre = EncDecCTCModelBPE.from_config_dict(cfg.preprocessor)
    pre.to(asr_model.device).eval()
    return pre


# ===============================
# Nemotron Streamer
# ===============================

class NemotronStreamer:
    def __init__(self):
        print("[INIT] Loading Nemotron...")
        self.model = nemo_asr.models.ASRModel.from_pretrained(model_name=MODEL_NAME).to(DEVICE).eval()

        decoding_cfg = self.model.cfg.decoding
        with open_dict(decoding_cfg):
            decoding_cfg.strategy = "greedy"
        self.model.change_decoding_strategy(decoding_cfg)

        self.preprocessor = init_streaming_preprocessor(self.model)
        self.pre_encode_cache_size = int(self.model.encoder.streaming_cfg.pre_encode_cache_size[1])
        self.num_feat = int(self.model.cfg.preprocessor.features)

        self.reset()

        # 🔥 Warmup
        print("[INIT] Warming up model...")
        dummy = np.zeros(ASR_CHUNK_SAMPLES, dtype=np.int16)
        self.stream_step(dummy)
        self.reset()
        print("[INIT] Warmup complete.")

    def reset(self):
        self.cache_last_channel, self.cache_last_time, self.cache_last_channel_len = (
            self.model.encoder.get_initial_cache_state(batch_size=1)
        )
        self.previous_hypotheses = None
        self.pred_out_stream = None
        self.cache_pre_encode = torch.zeros((1, self.num_feat, self.pre_encode_cache_size), device=DEVICE)
        self._last_text = ""

    def stream_step(self, pcm16: np.ndarray):
        audio_f32 = pcm16.astype(np.float32) / 32768.0
        audio_signal = torch.from_numpy(audio_f32).unsqueeze(0).to(DEVICE)
        audio_len = torch.tensor([audio_f32.shape[0]], device=DEVICE)

        processed_signal, processed_signal_length = self.preprocessor(audio_signal, audio_len)

        processed_signal = torch.cat([self.cache_pre_encode, processed_signal], dim=-1)
        processed_signal_length += self.cache_pre_encode.shape[2]
        self.cache_pre_encode = processed_signal[:, :, -self.pre_encode_cache_size:]

        with torch.no_grad():
            (
                self.pred_out_stream,
                transcribed_texts,
                self.cache_last_channel,
                self.cache_last_time,
                self.cache_last_channel_len,
                self.previous_hypotheses,
            ) = self.model.conformer_stream_step(
                processed_signal=processed_signal,
                processed_signal_length=processed_signal_length,
                cache_last_channel=self.cache_last_channel,
                cache_last_time=self.cache_last_time,
                cache_last_channel_len=self.cache_last_channel_len,
                previous_hypotheses=self.previous_hypotheses,
                previous_pred_out=self.pred_out_stream,
                return_transcription=True,
            )

        text = extract_transcriptions(transcribed_texts)[0]
        self._last_text = text

        if DEBUG_ASR:
            print(f"[ASR] TEXT: '{text}'")

        return text

    @property
    def last_text(self):
        return self._last_text


# ===============================
# Silero VAD
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
    speech_ms: int = 0
    silence_ms: int = 0


# ===============================
# Load models
# ===============================

asr = NemotronStreamer()


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
                print(f"[AUDIO] Received {len(data)} bytes")

            chunk = np.frombuffer(data, dtype=np.int16)
            vad_buf = np.concatenate([vad_buf, chunk])
            asr_buf = np.concatenate([asr_buf, chunk])

            # ---- VAD ----
            end_utt = False

            while len(vad_buf) >= VAD_FRAME_SAMPLES:
                frame = vad_buf[:VAD_FRAME_SAMPLES]
                vad_buf = vad_buf[VAD_FRAME_SAMPLES:]

                p = silero_prob(frame)

                if DEBUG_VAD:
                    print(f"[VAD] prob={p:.3f}")

                if not vad_state.speaking:
                    if p > VAD_START_TH:
                        vad_state.speaking = True
                        print("[VAD] SPEECH START")
                else:
                    if p < VAD_END_TH:
                        vad_state.speaking = False
                        end_utt = True
                        print("[VAD] SPEECH END")

            # ---- ASR ----
            if vad_state.speaking:
                while len(asr_buf) >= ASR_CHUNK_SAMPLES:
                    chunk = asr_buf[:ASR_CHUNK_SAMPLES]
                    asr_buf = asr_buf[ASR_CHUNK_SAMPLES:]

                    text = asr.stream_step(chunk)

                    if text:
                        await ws.send_text(json.dumps({"type": "partial", "text": text}))

            if end_utt:
                final_text = asr.last_text
                print(f"[FINAL] '{final_text}'")
                await ws.send_text(json.dumps({"type": "final", "text": final_text}))
                asr.reset()

    except WebSocketDisconnect:
        print("Client disconnected")
