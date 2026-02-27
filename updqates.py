websockets.exceptions.ConnectionClosedError: no close frame received or sent
(nemo) PS C:\Users\re_nikitav\Documents\nemotron_silero> python .\client.py
🎙️ Speak now... Ctrl+C to stop
[ERROR] Object of type Hypothesis is not JSON serializable
(nemo) PS C:\Users\re_nikitav\Documents\nemotron_silero>

server logs-
Transcribing: 100%|██████████| 1/1 [00:00<00:00, 27.45it/s]
2026-02-27 09:07:26,476 | DEBUG | ASR_SERVER | ASR | PARTIAL samples=0 text='Hypothesis(score=0.0, y_sequence=tensor([], dtype=torch.int64), text='', dec_out=None, dec_state=None, timestamp=[], alignments=None, frame_confidence=None, token_confidence=None, word_confidence=None, length=0, y=None, lm_state=None, lm_scores=None, ngram_lm_state=None, tokens=None, last_token=None, token_duration=None, last_frame=None, biasing_cfg=None, xatt_scores=None)'
2026-02-27 09:07:26,476 | ERROR | ASR_SERVER | WS | ERROR: Object of type Hypothesis is not JSON serializable
Traceback (most recent call last):
  File "/app/server.py", line 174, in ws_asr
    await ws.send_text(json.dumps({"type": "partial", "text": text}))
  File "/usr/lib/python3.10/json/__init__.py", line 231, in dumps
    return _default_encoder.encode(obj)
  File "/usr/lib/python3.10/json/encoder.py", line 199, in encode
    chunks = self.iterencode(o, _one_shot=True)
  File "/usr/lib/python3.10/json/encoder.py", line 257, in iterencode
    return _iterencode(o, 0)
  File "/usr/lib/python3.10/json/encoder.py", line 179, in default
    raise TypeError(f'Object of type {o.__class__.__name__} '
TypeError: Object of type Hypothesis is not JSON serializable
INFO:     connection closed
