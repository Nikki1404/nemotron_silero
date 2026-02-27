import asyncio
import json
import numpy as np
import sounddevice as sd
import websockets

WS_URL = "ws://127.0.0.1:8000/ws"
SR = 16000
BLOCK_MS = 40
BLOCK_SAMPLES = int(SR * BLOCK_MS / 1000)


async def run():
    print("🎙️ Speak now... Ctrl+C to stop")

    async with websockets.connect(WS_URL, ping_interval=20, ping_timeout=20) as ws:
        q = asyncio.Queue()

        def callback(indata, frames, time_info, status):
            if status:
                # print(status)  # optional
                pass
            # float32 [-1,1] -> int16
            pcm16 = (np.clip(indata[:, 0], -1.0, 1.0) * 32767.0).astype(np.int16)
            q.put_nowait(pcm16.tobytes())

        stream = sd.InputStream(
            samplerate=SR,
            channels=1,
            dtype="float32",
            blocksize=BLOCK_SAMPLES,
            callback=callback,
        )

        with stream:
            recv_task = asyncio.create_task(receiver(ws))
            try:
                while True:
                    data = await q.get()
                    await ws.send(data)
            except KeyboardInterrupt:
                pass
            finally:
                recv_task.cancel()


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


if __name__ == "__main__":
    asyncio.run(run())
