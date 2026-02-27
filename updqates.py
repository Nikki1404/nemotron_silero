import asyncio
import json
import numpy as np
import sounddevice as sd
import websockets
import time

WS_URL = "ws://127.0.0.1:8000/ws"  # if server is on EC2, change this to ws://<EC2_PUBLIC_IP>:8000/ws
SR = 16000
BLOCK_MS = 40
BLOCK_SAMPLES = int(SR * BLOCK_MS / 1000)

def rms_db(x: np.ndarray) -> float:
    rms = float(np.sqrt(np.mean(x * x) + 1e-12))
    return 20.0 * np.log10(rms + 1e-12)

async def receiver(ws):
    try:
        while True:
            msg = await ws.recv()
            obj = json.loads(msg)

            if obj.get("type") == "partial":
                print("\r" + obj.get("text", ""), end="", flush=True)
            elif obj.get("type") == "final":
                print("\n[FINAL] " + obj.get("text", ""))
            elif obj.get("type") == "error":
                print("\n[ERROR] " + obj.get("message", ""))
    except websockets.exceptions.ConnectionClosed:
        print("\n[INFO] Connection closed.")

async def run():
    print("🎙️ Speak now... Ctrl+C to stop")

    async with websockets.connect(WS_URL, ping_interval=20, ping_timeout=20) as ws:
        recv_task = asyncio.create_task(receiver(ws))

        last_lvl = time.time()

        def callback(indata, frames, time_info, status):
            nonlocal last_lvl
            if status:
                pass
            mono = indata[:, 0].astype(np.float32)
            if time.time() - last_lvl >= 1.0:
                last_lvl = time.time()
                print(f"\n[MIC] level={rms_db(mono):.1f} dB", end="")

            pcm16 = (np.clip(mono, -1.0, 1.0) * 32767.0).astype(np.int16)
            asyncio.get_event_loop().call_soon_threadsafe(
                lambda: asyncio.create_task(ws.send(pcm16.tobytes()))
            )

        stream = sd.InputStream(
            samplerate=SR,
            channels=1,
            dtype="float32",
            blocksize=BLOCK_SAMPLES,
            callback=callback,
        )

        try:
            with stream:
                while True:
                    await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            recv_task.cancel()

if __name__ == "__main__":
    asyncio.run(run())
