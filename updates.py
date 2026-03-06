FROM python:3.11-slim

ARG USE_PROXY=false

WORKDIR /srv

COPY requirements.txt .

RUN if [ "$USE_PROXY" = "true" ]; then \
        echo "Enabling proxy"; \
        export http_proxy=http://163.116.128.80:8080; \
        export https_proxy=http://163.116.128.80:8080; \
    fi && \
    pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

COPY download_model/nemotron-speech-streaming/nemotron-speech-streaming-en-0.6b.nemo .
COPY app ./app
COPY app/google_credentials.json google_credentials.json

ENV GOOGLE_APPLICATION_CREDENTIALS=/srv/google_credentials.json
ENV GOOGLE_RECOGNIZER=projects/eci-ugi-digital-ccaipoc/locations/us-central1/recognizers/google-stt-default
ENV GOOGLE_REGION=us-central1
ENV GOOGLE_LANGUAGE=en-US
ENV GOOGLE_MODEL=latest_short
ENV GOOGLE_INTERIM=true
ENV GOOGLE_EXPLICIT_DECODING=true

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]


getting this after docker run 

DEBUG: Startup cfg.model_name='nemotron-speech-streaming-en-0.6b.nemo' cfg.asr_backend='nemotron'
Loading whisper (openai/whisper-large-v3-turbo)...
Loading nemotron (nemotron-speech-streaming-en-0.6b.nemo)...
[NeMo I 2026-03-06 10:34:20 nemo_logging:393] Tokenizer SentencePieceTokenizer initialized with 1024 tokens
[NeMo W 2026-03-06 10:34:21 nemo_logging:405] If you intend to do training or fine-tuning, please call the ModelPT.setup_training_data() method and provide a valid configuration file to setup the train data loader.
    Train config :
    use_lhotse: true
    skip_missing_manifest_entries: true
    input_cfg: null
    tarred_audio_filepaths: null
    manifest_filepath: null
    sample_rate: 16000
    shuffle: true
    num_workers: 2
    pin_memory: true
    max_duration: 40.0
    min_duration: 0.1
    text_field: answer
    batch_duration: null
    use_bucketing: true
    max_tps: null
    bucket_duration_bins: null
    bucket_batch_size: null
    num_buckets: null
    bucket_buffer_size: null
    shuffle_buffer_size: null
    augmentor: null

[NeMo W 2026-03-06 10:34:21 nemo_logging:405] If you intend to do validation, please call the ModelPT.setup_validation_data() or ModelPT.setup_multiple_validation_data() method and provide a valid configuration file to setup the validation data loader(s).
    Validation config :
    use_lhotse: true
    manifest_filepath: /data/ASR/en/librispeech/test-other.json
    sample_rate: 16000
    batch_size: 32
    shuffle: false
    max_duration: 40.0
    min_duration: 0.1
    num_workers: 2
    pin_memory: true
    text_field: answer
    tarred_audio_filepaths: null

[NeMo I 2026-03-06 10:34:21 nemo_logging:393] PADDING: 0
[NeMo I 2026-03-06 10:34:25 nemo_logging:393] Using RNNT Loss : warprnnt_numba
    Loss warprnnt_numba_kwargs: {'fastemit_lambda': 0.005, 'clamp': -1.0}
[NeMo I 2026-03-06 10:34:25 nemo_logging:393] Using RNNT Loss : warprnnt_numba
    Loss warprnnt_numba_kwargs: {'fastemit_lambda': 0.005, 'clamp': -1.0}
[NeMo I 2026-03-06 10:34:25 nemo_logging:393] Using RNNT Loss : warprnnt_numba
    Loss warprnnt_numba_kwargs: {'fastemit_lambda': 0.005, 'clamp': -1.0}
[NeMo I 2026-03-06 10:34:28 nemo_logging:393] Model EncDecRNNTBPEModel was successfully restored from /srv/nemotron-speech-streaming-en-0.6b.nemo.
[NeMo I 2026-03-06 10:34:28 nemo_logging:393] Using RNNT Loss : warprnnt_numba
    Loss warprnnt_numba_kwargs: {'fastemit_lambda': 0.005, 'clamp': -1.0}
[NeMo I 2026-03-06 10:34:28 nemo_logging:393] Changed decoding strategy to
    model_type: rnnt
    strategy: greedy
    compute_hypothesis_token_set: false
    preserve_alignments: null
    tdt_include_token_duration: null
    confidence_cfg:
      preserve_frame_confidence: false
      preserve_token_confidence: false
      preserve_word_confidence: false
      exclude_blank: true
      aggregation: min
      tdt_include_duration: false
      method_cfg:
        name: entropy
        entropy_type: tsallis
        alpha: 0.33
        entropy_norm: exp
        temperature: DEPRECATED
    fused_batch_size: null
    compute_timestamps: null
    compute_langs: false
    word_seperator: ' '
    segment_seperators:
    - .
    - '!'
    - '?'
    segment_gap_threshold: null
    rnnt_timestamp_type: all
    greedy:
      max_symbols_per_step: 10
      preserve_alignments: false
      preserve_frame_confidence: false
      tdt_include_token_duration: false
      tdt_include_duration_confidence: false
      confidence_method_cfg:
        name: entropy
        entropy_type: tsallis
        alpha: 0.33
        entropy_norm: exp
        temperature: DEPRECATED
      loop_labels: false
      use_cuda_graph_decoder: false
      max_symbols: 10
    beam:
      beam_size: 4
      search_type: default
      score_norm: true
      return_best_hypothesis: true
      tsd_max_sym_exp_per_step: 50
      alsd_max_target_len: 1.0
      nsc_max_timesteps_expansion: 1
      nsc_prefix_alpha: 1
      maes_num_steps: 2
      maes_prefix_alpha: 1
      maes_expansion_gamma: 2.3
      maes_expansion_beta: 2
      language_model: null
      softmax_temperature: 1.0
      preserve_alignments: false
      ngram_lm_model: null
      ngram_lm_alpha: 0.0
      hat_subtract_ilm: false
      hat_ilm_weight: 0.0
    temperature: 1.0
    durations: []
    big_blank_durations: []

2026-03-06 10:34:29,603 - ERROR - Failed to preload nemotron: name 'http_proxy' is not defined
2026-03-06 10:34:29,720 - ERROR - Failed to preload google: name 'http_proxy' is not defined
2026-03-06 10:34:29,720 - INFO - All engines preloaded.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8003 (Press CTRL+C to quit)
(base) root@EC03-E01-AICOE1:/home/CORP/re_nikitav/asr-realtime-custom-vad-download#
and also modified main from this 
#main.py-
#app/main.py-
import asyncio
import json
import time
import logging
import os
import numpy as np
import resampy

from fastapi import FastAPI, WebSocket

from app.config import load_config, Config, MODEL_MAP
from app.vad import AdaptiveEnergyVAD
from app.factory import build_engine
from app.asr_engines.base import ASREngine

cfg = load_config()
logging.basicConfig(level=cfg.log_level, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("asr_server")

app = FastAPI()
ENGINE_CACHE: dict[str, ASREngine] = {}


async def preload_engines():
    backends = ["whisper", "nemotron", "google"]
    log.info("Preloading ASR engines...")

    for backend in backends:
        try:
            model_name = MODEL_MAP[backend]
            print(f"Loading {backend} ({model_name})...")

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

            log.info(f"Preloaded {backend} in {load_sec:.2f}s")
            ENGINE_CACHE[backend] = engine

        except Exception as e:
            log.error(f"Failed to preload {backend}: {e}")
            continue

    log.info("All engines preloaded.")


@app.on_event("startup")
async def startup_event():
    await preload_engines()


def get_engine(backend: str) -> ASREngine:
    if backend not in ENGINE_CACHE:
        raise ValueError(f"Engine '{backend}' not preloaded. Available: {list(ENGINE_CACHE.keys())}")
    log.info(f"Using cached {backend} engine")
    return ENGINE_CACHE[backend]


@app.websocket("/asr/realtime-custom-vad")
async def ws_asr(ws: WebSocket):
    await ws.accept()

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

            # EOS from client
            if data == b"":
                if utt_started:
                    final = session.finalize(cfg.post_speech_pad_ms)
                    await _emit_final(ws, final, t_utt_start, t_first_partial)
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

                # PARTIALS
                if engine.caps.partials:
                    text = session.step_if_ready()
                    if text:
                        if t_first_partial is None:
                            t_first_partial = time.time()

                        ttfb_ms = int((t_first_partial - t_utt_start) * 1000)

                        await ws.send_text(json.dumps({
                            "type": "partial",
                            "text": text,
                            "t_start": ttfb_ms
                        }))

                # ENDPOINT
                if (
                    not is_speech
                    and utt_audio_ms >= cfg.min_utt_ms
                    and silence_ms >= cfg.end_silence_ms
                ):
                    final = session.finalize(cfg.post_speech_pad_ms)
                    await _emit_final(ws, final, t_utt_start, t_first_partial)

                    vad.reset()
                    utt_started = False
                    utt_audio_ms = 0
                    silence_ms = 0

    finally:
        await ws.close()
        log.info("WS disconnected")


async def _emit_final(ws, final_text, t_start, t_first_partial):
    if not final_text:
        return

    ttfb_ms = (
        int((t_first_partial - t_start) * 1000)
        if (t_first_partial and t_start)
        else None
    )

    await ws.send_text(json.dumps({
        "type": "final",
        "text": final_text,
        "t_start": ttfb_ms
    }))

to this 
#main.py-
#app/main.py-
import asyncio
import json
import time
import logging
import os
import numpy as np
import resampy

from fastapi import FastAPI, WebSocket

from app.config import load_config, Config, MODEL_MAP
from app.vad import AdaptiveEnergyVAD
from app.factory import build_engine
from app.asr_engines.base import ASREngine

cfg = load_config()
logging.basicConfig(level=cfg.log_level, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("asr_server")

app = FastAPI()
ENGINE_CACHE: dict[str, ASREngine] = {}


async def preload_engines():
    backends = ["whisper", "nemotron", "google"]
    log.info("Preloading ASR engines...")

    for backend in backends:
        try:
            model_name = MODEL_MAP[backend]
            print(f"Loading {backend} ({model_name})...")

            tmp_cfg = Config()
            object.__setattr__(tmp_cfg, 'asr_backend', backend)
            object.__setattr__(tmp_cfg, 'model_name', model_name)
            object.__setattr__(tmp_cfg, 'device', cfg.device)
            object.__setattr__(tmp_cfg, 'sample_rate', cfg.sample_rate)
            object.__setattr__(tmp_cfg, 'context_right', cfg.context_right)

            engine = build_engine(tmp_cfg)
            load_sec = engine.load()

            if(http_proxy in os.environ):
                os.environ.pop("https_proxy", None)
                os.environ.pop("http_proxy", None)

            log.info(f"Preloaded {backend} in {load_sec:.2f}s")
            ENGINE_CACHE[backend] = engine

        except Exception as e:
            log.error(f"Failed to preload {backend}: {e}")
            continue

    log.info("All engines preloaded.")


@app.on_event("startup")
async def startup_event():
    await preload_engines()


def get_engine(backend: str) -> ASREngine:
    if backend not in ENGINE_CACHE:
        raise ValueError(f"Engine '{backend}' not preloaded. Available: {list(ENGINE_CACHE.keys())}")
    log.info(f"Using cached {backend} engine")
    return ENGINE_CACHE[backend]


@app.websocket("/asr/realtime-custom-vad")
async def ws_asr(ws: WebSocket):
    await ws.accept()

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

            # EOS from client
            if data == b"":
                if utt_started:
                    final = session.finalize(cfg.post_speech_pad_ms)
                    await _emit_final(ws, final, t_utt_start, t_first_partial)
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

                # PARTIALS
                if engine.caps.partials:
                    text = session.step_if_ready()
                    if text:
                        if t_first_partial is None:
                            t_first_partial = time.time()

                        ttfb_ms = int((t_first_partial - t_utt_start) * 1000)

                        await ws.send_text(json.dumps({
                            "type": "partial",
                            "text": text,
                            "t_start": ttfb_ms
                        }))

                # ENDPOINT
                if (
                    not is_speech
                    and utt_audio_ms >= cfg.min_utt_ms
                    and silence_ms >= cfg.end_silence_ms
                ):
                    final = session.finalize(cfg.post_speech_pad_ms)
                    await _emit_final(ws, final, t_utt_start, t_first_partial)

                    vad.reset()
                    utt_started = False
                    utt_audio_ms = 0
                    silence_ms = 0

    finally:
        await ws.close()
        log.info("WS disconnected")


async def _emit_final(ws, final_text, t_start, t_first_partial):
    if not final_text:
        return

    ttfb_ms = (
        int((t_first_partial - t_start) * 1000)
        if (t_first_partial and t_start)
        else None
    )

    await ws.send_text(json.dumps({
        "type": "final",
        "text": final_text,
        "t_start": ttfb_ms
    }))

