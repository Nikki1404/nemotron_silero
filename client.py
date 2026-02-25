import asyncio
import json
import sys
import time

import numpy as np
import sounddevice as sd
import websockets

SR = 16000
CHUNK_MS = 80
CHUNK_SAMPLES = int(SR * CHUNK_MS / 1000)

# Change to: ws://EC2_PUBLIC_IP:8000/ws
WS_URL = "ws://127.0.0.1:8000/ws"


async def run():
    async with websockets.connect(WS_URL, max_size=2**24) as ws:
        loop = asyncio.get_running_loop()

        last_line = ""
        last_print = 0.0

        def callback(indata, frames, time_info, status):
            if status:
                pass
            x = np.clip(indata[:, 0], -1.0, 1.0)
            pcm16 = (x * 32767.0).astype(np.int16)
            # send raw PCM16 bytes
            loop.call_soon_threadsafe(asyncio.create_task, ws.send(pcm16.tobytes()))

        print("🎙️ Speak now... Ctrl+C to stop")
        with sd.InputStream(
            samplerate=SR,
            channels=1,
            dtype="float32",
            blocksize=CHUNK_SAMPLES,
            callback=callback,
        ):
            while True:
                msg = await ws.recv()
                obj = json.loads(msg)
                t = obj.get("type")

                if t == "partial":
                    txt = obj.get("text", "")
                    # keep console smooth
                    now = time.time()
                    if txt != last_line or (now - last_print) > 0.2:
                        sys.stdout.write("\r" + txt + " " * 20)
                        sys.stdout.flush()
                        last_line = txt
                        last_print = now

                elif t == "final":
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    print("[FINAL]", obj.get("text", ""))

                elif t == "warn":
                    # optional
                    pass

                elif t == "error":
                    print("[ERROR]", obj.get("message", "unknown"))
                    break


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\nStopped.")