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
