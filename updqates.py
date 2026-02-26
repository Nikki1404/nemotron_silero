#router.py-
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import logging
import torch
import io
import os
import soundfile as sf

from kokoro import KPipeline

router  = APIRouter(prefix="/v1")


MODEL = None

def get_model():
    global MODEL
    if MODEL is None:
        if torch.cuda.is_available():
            DEVICE = "cuda"
        else:
            DEVICE = "cpu"

        MODEL = KPipeline(lang_code='a', device=DEVICE)
    return MODEL

def audio_generator(text: str, voice: str = 'af_heart'):
    model = get_model()
    generator = model(text, voice=voice, speed=1, split_pattern=r'\n+')
    
    for _, _, audio in generator:
        # Convert numpy array to bytes (e.g., WAV format)
        with io.BytesIO() as buffer:
            sf.write(buffer, audio, 24000, format='WAV')
            yield buffer.getvalue()


class TextInput(BaseModel):
    input: str = Field(..., description="Text to synthesize")

@router.post("/tts/audio/speech")
async def audio_speech(body: TextInput):
    try:
        text = (body.input or "").strip()
        return StreamingResponse(audio_generator(text), media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)

#main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from router import router


app = FastAPI()

app.include_router(router)

# client.py-

from openai import OpenAI
import numpy as np
import soundfile as sf

client = OpenAI(
    base_url="https://tts-kokoro-openapi-150916788856.europe-west1.run.app/v1/tts",
    api_key="not-needed",
)

pcm_path = "output.pcm"
wav_path = "output.wav"

# 1️⃣ Save PCM
with client.audio.speech.with_streaming_response.create(
    model="",
    voice="",
    input="Hello world from kokoro openapi deployed on gcp without docker testing",
) as resp:

    with open(pcm_path, "wb") as f:
        for chunk in resp.iter_bytes():
            f.write(chunk)

print("Saved -> output.pcm")

# 2️⃣ Convert PCM → WAV
with open(pcm_path, "rb") as f:
    pcm_data = f.read()

audio = np.frombuffer(pcm_data, dtype=np.int16)

# Convert to float32 range (-1 to 1) for WAV writing
audio_float = audio.astype(np.float32) / 32767.0

sf.write(wav_path, audio_float, 24000, format="WAV")

print("Converted -> output.wav")

#Dockerfile-
# CUDA runtime base image
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

ENV HF_HOME=/root/.cache/huggingface
ENV TRANSFORMERS_CACHE=/root/.cache/huggingface
ENV HF_HUB_ENABLE_HF_TRANSFER=1

RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install --no-cache-dir \
    torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cu121

RUN python3 -m pip install --no-cache-dir \
    transformers \
    huggingface_hub

RUN python3 - <<EOF
from huggingface_hub import snapshot_download
snapshot_download(repo_id="hexgrad/Kokoro-82M")
EOF

COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY main.py /app
COPY router.py /app

EXPOSE 8080

CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

#requirements.txt

kokoro
fastapi
numpy
soundfile
torch
uvicorn
websockets
