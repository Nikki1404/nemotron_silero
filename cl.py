import asyncio
import json
import time
import numpy as np
import sounddevice as sd
import websockets

WS_URL = "ws://127.0.0.1:8000/ws"
SR = 16000
BLOCK_MS = 40
BLOCK_SAMPLES = int(SR * BLOCK_MS / 1000)

first_audio_sent_ts = None
ttfb_reported = False


def rms_db(x: np.ndarray) -> float:
    rms = float(np.sqrt(np.mean(x * x) + 1e-12))
    return 20.0 * np.log10(rms + 1e-12)


async def receiver(ws):
    global first_audio_sent_ts, ttfb_reported

    try:
        while True:
            msg = await ws.recv()
            obj = json.loads(msg)

            # ---- TTFB calculation ----
            if not ttfb_reported and obj.get("type") in ["partial", "final"]:
                if first_audio_sent_ts is not None:
                    ttfb_ms = (time.time() - first_audio_sent_ts) * 1000
                    print(f"\n[TTFB] {ttfb_ms:.2f} ms")
                    ttfb_reported = True

            if obj.get("type") == "partial":
                print("\r" + obj.get("text", ""), end="", flush=True)

            elif obj.get("type") == "final":
                print("\n[FINAL] " + obj.get("text", ""))

                # reset for next utterance
                ttfb_reported = False
                first_audio_sent_ts = None

            elif obj.get("type") == "error":
                print("\n[ERROR] " + obj.get("message", ""))

    except websockets.exceptions.ConnectionClosed:
        print("\n[INFO] Connection closed.")


async def run():
    global first_audio_sent_ts

    print("🎙️ Speak now... Ctrl+C to stop")

    loop = asyncio.get_running_loop()
    send_q: asyncio.Queue[bytes] = asyncio.Queue(maxsize=50)

    async with websockets.connect(WS_URL, ping_interval=20, ping_timeout=20) as ws:

        recv_task = asyncio.create_task(receiver(ws))

        async def sender():
            global first_audio_sent_ts
            try:
                while True:
                    data = await send_q.get()

                    # start TTFB timer when first audio is sent
                    if first_audio_sent_ts is None:
                        first_audio_sent_ts = time.time()

                    await ws.send(data)

            except asyncio.CancelledError:
                return

        send_task = asyncio.create_task(sender())

        last_lvl = 0.0

        def callback(indata, frames, time_info, status):
            nonlocal last_lvl

            if status:
                pass

            mono = indata[:, 0].astype(np.float32)

            now = time.time()
            if now - last_lvl >= 1.0:
                last_lvl = now
                lvl = rms_db(mono)
                loop.call_soon_threadsafe(
                    lambda: print(f"\n[MIC] level={lvl:.1f} dB", end="")
                )

            pcm16 = (np.clip(mono, -1.0, 1.0) * 32767.0).astype(np.int16)
            payload = pcm16.tobytes()

            def _enqueue():
                if not send_q.full():
                    send_q.put_nowait(payload)

            loop.call_soon_threadsafe(_enqueue)

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
            send_task.cancel()


if __name__ == "__main__":
    asyncio.run(run())
