Improvements Done in Nemotron + Silero VAD

• Pre-roll buffering (250 ms) added to capture audio just before speech starts.
→ Prevents missing initial phonemes of words.

• Post-roll buffering (350 ms) added after silence detection.
→ Ensures last words are not truncated.

• Minimum speech duration threshold (~700 ms) implemented.
→ Avoids sending very short noises or breaths to ASR.

• Improved silence detection (~800 ms) before finalizing an utterance.
→ Creates cleaner speech segmentation.

• Model preloading / caching enabled.
→ Nemotron ASR loads once at startup, eliminating first-request latency.

• More stable utterance segmentation due to VAD-driven speech boundary detection.

Benchmarking Observation

Custom VAD

• Slightly lower latency (faster TTFB).
• Simpler energy-based detection.

Silero VAD

• Slightly higher latency due to buffering and detection logic.
• More stable speech segmentation.
• Reduces unnecessary ASR calls.

Recommendation Based on Benchmark

For scalable production systems:

➡ Nemotron + Silero VAD is the better choice.

Reason:

• More robust speech detection.
• Better utterance boundaries.
• Lower ASR compute load at scale.
• More stable performance in noisy environments.

Custom VAD may still be useful for ultra-low latency use cases, but Silero VAD is preferable for scalable real-time ASR systems.
