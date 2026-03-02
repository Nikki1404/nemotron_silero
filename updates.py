Custom VAD achieves significantly better accuracy (WER ≈ 0.11) compared to Silero (WER ≈ 0.33), a ~66% relative improvement. The gain remains ~3× better even after normalization, confirming it is not formatting-related.
Latency is similar for both systems (~9.8 seconds), with no meaningful difference.
Custom VAD also shows better stability (10/15 files improved), while Silero had multiple high-error cases (WER = 1.0), likely due to earlier speech segmentation affecting RNNT context.
Further tuning of Silero VAD (thresholds and buffering) may help reduce the accuracy gap.
