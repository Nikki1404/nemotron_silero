Nemotron + Custom VAD vs Nemotron + Silero — Summary

Accuracy
Custom VAD mean WER ≈ 0.11
Silero mean WER ≈ 0.33
Approximately 66% relative improvement with Custom VAD

Normalized Accuracy
Custom VAD remains ~3× better after normalization
Improvement is not due to punctuation or formatting differences

Latency
Both systems average around 9.8 seconds
No meaningful latency difference observed

Stability
Custom VAD performed better in 10 out of 15 files
Silero showed multiple high-error cases (WER = 1.0)

Technical Observation
Silero tends to segment speech earlier, which can negatively affect RNNT decoding context
Custom VAD maintains longer, cleaner utterance segments, leading to more consistent transcription quality

Next Steps
Further tuning and segmentation control on top of Silero VAD may reduce the current accuracy gap. I can investigate whether threshold calibration, buffering adjustments, and segmentation refinements bring its performance closer to the custom VAD approach.
