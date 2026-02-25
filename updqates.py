import websockets
from pathlib import Path
from typing import Optional, List, Tuple
import json
import asyncio
import wave
import time

import jiwer
import util
import pandas as pd
from tqdm import tqdm
from whisper_normalizer.english import EnglishTextNormalizer


URL = "ws://127.0.0.1:8000/ws"
DATA_FOLDER = Path("asr-realtime-benchmarking-data")

TARGET_SR = 16000
CHUNK_MS = 80
CHUNK_FRAMES = int(TARGET_SR * CHUNK_MS / 1000)



whisper_norm = EnglishTextNormalizer()
def normalize(txt):
    return whisper_norm(txt or "")


def iter_wav_chunks(path: Path):
    with wave.open(str(path), "rb") as wf:
        while True:
            data = wf.readframes(CHUNK_FRAMES)
            if not data:
                break
            yield data

def silence_bytes(sec: float) -> bytes:
    return b"\x00\x00" * int(TARGET_SR * sec)

async def transcribe_ws(
    *,
    backend: str,
    wav_path: Path,
) -> Tuple[str, float, int]:

    async with websockets.connect(URL, max_size=None) as ws:
        await ws.send(json.dumps({
            "type": "config",
            "backend": backend,
            "sampling_rate": TARGET_SR,
            "chunk_ms": CHUNK_MS,
        }))

        finals = []
        final_received = asyncio.Event()

        async def receiver():
            async for msg in ws:
                if isinstance(msg, str):
                    obj = json.loads(msg)
                    if obj.get("type") == "final":
                        if obj.get("text"):
                            finals.append(obj["text"].strip())
                        final_received.set()

        recv_task = asyncio.create_task(receiver())

        frames_sent = 0
        audio_sec_sent = 0.0

        t_start = time.time()

        for chunk in iter_wav_chunks(wav_path):
            await ws.send(chunk)
            frames_sent += len(chunk) // 2
            audio_sec_sent = frames_sent / TARGET_SR

        # finalize
        await ws.send(silence_bytes(0.6))
        await ws.send(b"")

        await asyncio.wait_for(final_received.wait(), timeout=30)

        latency_ms = int((time.time() - t_start) * 1000)

        await ws.close()
        recv_task.cancel()

        return " ".join(finals), audio_sec_sent, latency_ms

def get_reference_text(txt_path: Path) -> str:
    with open(txt_path, "r", encoding="utf-8") as file:
        content = file.read()
    return content

async def get_benchmark_result(wav_path: Path, ref: str, backend: str) -> dict:
    try:
        hyp, audio_sec, latency_ms = await transcribe_ws(
            backend=backend,
            wav_path=wav_path,
        )
        return latency_ms, hyp
    except Exception as e:
        print("error: ", e)
        return None


transform = jiwer.Compose([
    jiwer.ToLowerCase(),
    jiwer.RemovePunctuation(),
    jiwer.RemoveMultipleSpaces(),
    jiwer.Strip(),
    jiwer.ReduceToListOfListOfWords(word_delimiter=" "),
])
def calculate_wer(reference_str: str, hypothesis_str: str) -> float:
    wer = jiwer.wer(reference=reference_str, hypothesis=hypothesis_str, reference_transform=transform, hypothesis_transform=transform)
    return wer


def get_service_results(wav_path: Path, text: str):
    service_results = {}
    service_results[util.REFERENCE_TEXT_COLUMN_NAME] = text
    reference_text_normalized = normalize(text)
    service_results[util.REFERENCE_TEXT_NORMALIZED_COLUMN_NAME] = reference_text_normalized

    for model in util.MODELS:
        latency, transcript = asyncio.run(get_benchmark_result(wav_path=wav_path, ref=text, backend=model))
        service_results[util.get_latency_column_name(model)] = latency
        service_results[util.get_transcript_column_name(model)] = transcript
        service_results[util.get_wer_column_name(model)] = calculate_wer(text, transcript)

        normalized_transcript = normalize(transcript)
        service_results[util.get_transcript_normalized_column_name(model)] = normalized_transcript
        service_results[util.get_wer_for_transcript_and_reference_normalized_column_name(model)] = calculate_wer(reference_text_normalized, normalized_transcript)

    return service_results

def get_result_from_service():
    result_dataset = {}
    for subfolder in tqdm(DATA_FOLDER.iterdir(), total=len(list(DATA_FOLDER.iterdir()))):
        if subfolder.is_dir():
            print(subfolder)
            wav_path = next(subfolder.glob("*.wav"), None)
            txt_path = next(subfolder.glob("*.txt"), None)

            reference_text = get_reference_text(txt_path)

            if wav_path and txt_path:
                try:
                    result_dataset[subfolder.name] = get_service_results(wav_path=wav_path, text=reference_text)
                except Exception as e:
                    print(e)
    return result_dataset

def write_to_file(results):
    df = pd.DataFrame(results).T
    df.reset_index(inplace=True)
    df.rename(columns={"index": util.FILENAME_COLUMN_NAME}, inplace=True)
    column_order = util.get_column_order()
    df = df[column_order]
    df.to_excel('benchmark_results_asr_realtime.xlsx', index=True)

def main():
    result_dataset = get_result_from_service()
    write_to_file(result_dataset)

if __name__ == "__main__":
    main()

s3://cx-speech/asr-realtime/benchmarking-data-3/

Agree — let’s take 1–2 days to review the NIM and scaling details properly.

Since Nemotron requires external VAD for barge-in, getting a Silero + Nemotron sample (with/without barge-in) will help us validate real-time behavior faster. I’ll also compare NIM vs our current deployment from a latency standpoint.
