import asyncio
import json
import time
import copy  # ✅ FIX: use Python deepcopy
from dataclasses import dataclass
from typing import Optional

import numpy as np
import torch
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from omegaconf import OmegaConf, open_dict

import nemo.collections.asr as nemo_asr
from nemo.collections.asr.models.ctc_bpe_models import EncDecCTCModelBPE
from nemo.collections.asr.parts.utils.rnnt_utils import Hypothesis

# -----------------------------
# Low-latency config
# -----------------------------
SR = 16000

ASR_CHUNK_MS = 80
ASR_CHUNK_SAMPLES = int(SR * ASR_CHUNK_MS / 1000)

VAD_FRAME_SAMPLES = 512  # 32ms @ 16k

VAD_START_TH = 0.60
VAD_END_TH = 0.35
MIN_SPEECH_MS = 120
MIN_SILENCE_MS = 280
MAX_UTT_S = 20.0

PARTIAL_THROTTLE_S = 0.06
DROP_IF_BACKLOG_EXCEEDS_CHUNKS = 6

MODEL_NAME = "nvidia/nemotron-speech-streaming-en-0.6b"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

app = FastAPI()


@app.get("/health")
def health():
    return {"ok": True, "device": DEVICE, "model": MODEL_NAME, "sr": SR}


def extract_transcriptions(hyps):
    if not hyps:
        return [""]
    if isinstance(hyps[0], Hypothesis):
        return [h.text for h in hyps]
    return hyps


# ✅ FIXED HERE
def init_streaming_preprocessor(asr_model):
    cfg = copy.deepcopy(asr_model._cfg)
    OmegaConf.set_struct(cfg.preprocessor, False)
    cfg.preprocessor.dither = 0.0
    cfg.preprocessor.pad_to = 0
    cfg.preprocessor.normalize = "None"

    pre = EncDecCTCModelBPE.from_config_dict(cfg.preprocessor)
    pre.to(asr_model.device).eval()
    return pre


class NemotronStreamer:
    def __init__(self, model_name: str, device: str, right_context_frames: int = 0):
        self.device = torch.device(device)
        self.model = nemo_asr.models.ASRModel.from_pretrained(model_name=model_name).to(self.device).eval()

        try:
            left = int(self.model.encoder.att_context_size[0])
            self.model.encoder.set_default_att_context_size([left, int(right_context_frames)])
        except Exception:
            pass

        decoding_cfg = self.model.cfg.decoding
        with open_dict(decoding_cfg):
            decoding_cfg.strategy = "greedy"
            decoding_cfg.preserve_alignments = False
            if hasattr(decoding_cfg, "fused_batch_size"):
                decoding_cfg.fused_batch_size = -1
        self.model.change_decoding_strategy(decoding_cfg)

        self.preprocessor = init_streaming_preprocessor(self.model)
        self.pre_encode_cache_size = int(self.model.encoder.streaming_cfg.pre_encode_cache_size[1])
        self.num_feat = int(self.model.cfg.preprocessor.features)

        self.reset()

    def reset(self):
        self.cache_last_channel, self.cache_last_time, self.cache_last_channel_len = (
            self.model.encoder.get_initial_cache_state(batch_size=1)
        )
        self.previous_hypotheses = None
        self.pred_out_stream = None
        self.cache_pre_encode = torch.zeros((1, self.num_feat, self.pre_encode_cache_size), device=self.device)
        self._last_text = ""

    def stream_step_pcm16(self, pcm16: np.ndarray) -> str:
        audio_f32 = (pcm16.astype(np.float32) / 32768.0)
        audio_signal = torch.from_numpy(audio_f32).unsqueeze(0).to(self.device)
        audio_len = torch.tensor([audio_f32.shape[0]], device=self.device, dtype=torch.float32)

        processed_signal, processed_signal_length = self.preprocessor(input_signal=audio_signal, length=audio_len)

        processed_signal = torch.cat([self.cache_pre_encode, processed_signal], dim=-1)
        processed_signal_length = processed_signal_length + self.cache_pre_encode.shape[2]
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
                keep_all_outputs=False,
                previous_hypotheses=self.previous_hypotheses,
                previous_pred_out=self.pred_out_stream,
                drop_extra_pre_encoded=None,
                return_transcription=True,
            )

        text = extract_transcriptions(transcribed_texts)[0] if transcribed_texts is not None else ""
        self._last_text = text
        return text

    @property
    def last_text(self) -> str:
        return self._last_text


@dataclass
class VADState:
    speaking: bool = False
    speech_ms: int = 0
    silence_ms: int = 0
    utt_start_t: Optional[float] = None

    def reset(self):
        self.speaking = False
        self.speech_ms = 0
        self.silence_ms = 0
        self.utt_start_t = None


def pcm16_to_float32(x: np.ndarray) -> np.ndarray:
    return x.astype(np.float32) / 32768.0


print(f"[server] DEVICE={DEVICE}")
print("[server] Loading Nemotron...")
asr = NemotronStreamer(MODEL_NAME, DEVICE, right_context_frames=0)

print("[server] Loading Silero VAD...")
vad_model, _ = torch.hub.load(
    repo_or_dir="snakers4/silero-vad",
    model="silero_vad",
    trust_repo=True,
)

# ✅ Keep VAD on CPU for stability + lower latency
vad_device = torch.device("cpu")
vad_model.to(vad_device).eval()


def silero_prob_32ms(frame_pcm16: np.ndarray) -> float:
    x = pcm16_to_float32(frame_pcm16)
    xt = torch.from_numpy(x).to(vad_device)
    with torch.no_grad():
        return float(vad_model(xt, SR).item())


@app.websocket("/ws")
async def ws_asr(ws: WebSocket):
    await ws.accept()

    vad_state = VADState()
    vad_buf = np.zeros((0,), dtype=np.int16)
    asr_buf = np.zeros((0,), dtype=np.int16)

    incoming_chunks = 0
    last_sent = ""
    last_partial_ts = 0.0

    try:
        while True:
            data = await ws.receive_bytes()
            incoming_chunks += 1

            if incoming_chunks > DROP_IF_BACKLOG_EXCEEDS_CHUNKS:
                incoming_chunks = 0
                vad_buf = np.zeros((0,), dtype=np.int16)
                asr_buf = np.zeros((0,), dtype=np.int16)
                await ws.send_text(json.dumps({"type": "warn", "message": "Dropped audio to reduce latency"}))
                continue

            chunk = np.frombuffer(data, dtype=np.int16)
            vad_buf = np.concatenate([vad_buf, chunk])
            asr_buf = np.concatenate([asr_buf, chunk])

            end_utt = False
            while len(vad_buf) >= VAD_FRAME_SAMPLES:
                frame = vad_buf[:VAD_FRAME_SAMPLES]
                vad_buf = vad_buf[VAD_FRAME_SAMPLES:]

                p = silero_prob_32ms(frame)
                frame_ms = int(1000 * (VAD_FRAME_SAMPLES / SR))
                now = time.time()

                if not vad_state.speaking:
                    if p >= VAD_START_TH:
                        vad_state.speech_ms += frame_ms
                        if vad_state.speech_ms >= MIN_SPEECH_MS:
                            vad_state.speaking = True
                            vad_state.utt_start_t = now
                            vad_state.silence_ms = 0
                    else:
                        vad_state.speech_ms = 0
                else:
                    if p <= VAD_END_TH:
                        vad_state.silence_ms += frame_ms
                        if vad_state.silence_ms >= MIN_SILENCE_MS:
                            vad_state.speaking = False
                            vad_state.speech_ms = 0
                            end_utt = True
                    else:
                        vad_state.silence_ms = 0

                    if vad_state.utt_start_t and (now - vad_state.utt_start_t) >= MAX_UTT_S:
                        vad_state.speaking = False
                        end_utt = True

            if vad_state.speaking:
                while len(asr_buf) >= ASR_CHUNK_SAMPLES:
                    asr_chunk = asr_buf[:ASR_CHUNK_SAMPLES]
                    asr_buf = asr_buf[ASR_CHUNK_SAMPLES:]

                    text = asr.stream_step_pcm16(asr_chunk)
                    tnow = time.time()
                    if text and text != last_sent and (tnow - last_partial_ts) >= PARTIAL_THROTTLE_S:
                        await ws.send_text(json.dumps({"type": "partial", "text": text}))
                        last_sent = text
                        last_partial_ts = tnow
            else:
                if len(asr_buf) > ASR_CHUNK_SAMPLES:
                    asr_buf = asr_buf[-ASR_CHUNK_SAMPLES:]

            if end_utt:
                final_text = (asr.last_text or "").strip()
                await ws.send_text(json.dumps({"type": "final", "text": final_text}))

                asr.reset()
                vad_state.reset()
                last_sent = ""
                last_partial_ts = 0.0
                vad_buf = np.zeros((0,), dtype=np.int16)
                asr_buf = np.zeros((0,), dtype=np.int16)

            incoming_chunks = max(0, incoming_chunks - 1)

    except WebSocketDisconnect:
        return
    except Exception as e:
        try:
            await ws.send_text(json.dumps({"type": "error", "message": str(e)}))
        except Exception:
            pass
