 => [ 7/10] COPY  server_requirements.txt .                                                                                                            0.0s
 => [ 8/10] RUN python3 -m pip install --no-cache-dir -r server_requirements.txt                                                                     289.7s
 => ERROR [ 9/10] RUN python3 -c "import torch, torchaudio; torch.hub.load('snakers4/silero-vad','silero_vad',trust_repo=True); print('Silero cached'  5.3s
------
 > [ 9/10] RUN python3 -c "import torch, torchaudio; torch.hub.load('snakers4/silero-vad','silero_vad',trust_repo=True); print('Silero cached')":
3.578 Traceback (most recent call last):
3.578   File "/usr/local/lib/python3.10/dist-packages/torch/_ops.py", line 1442, in load_library
3.578     ctypes.CDLL(path)
3.578   File "/usr/lib/python3.10/ctypes/__init__.py", line 374, in __init__
3.579     self._handle = _dlopen(self._name, mode)
3.579 OSError: /usr/local/lib/python3.10/dist-packages/torchaudio/lib/libtorchaudio.so: undefined symbol: _ZNK5torch8autograd4Node4nameEv
3.579
3.579 The above exception was the direct cause of the following exception:
3.579
3.579 Traceback (most recent call last):
3.579   File "<string>", line 1, in <module>
3.579   File "/usr/local/lib/python3.10/dist-packages/torchaudio/__init__.py", line 2, in <module>
3.580     from . import _extension  # noqa  # usort: skip
3.580   File "/usr/local/lib/python3.10/dist-packages/torchaudio/_extension/__init__.py", line 38, in <module>
3.580     _load_lib("libtorchaudio")
3.580   File "/usr/local/lib/python3.10/dist-packages/torchaudio/_extension/utils.py", line 60, in _load_lib
3.581     torch.ops.load_library(path)
3.581   File "/usr/local/lib/python3.10/dist-packages/torch/_ops.py", line 1444, in load_library
3.581     raise OSError(f"Could not load this library: {path}") from e
3.581 OSError: Could not load this library: /usr/local/lib/python3.10/dist-packages/torchaudio/lib/libtorchaudio.so
------
Dockerfile:29
--------------------
  27 |     RUN python3 -m pip install --no-cache-dir -r server_requirements.txt
  28 |
  29 | >>> RUN python3 -c "import torch, torchaudio; torch.hub.load('snakers4/silero-vad','silero_vad',trust_repo=True); print('Silero cached')"
  30 |
  31 |     COPY server.py .
--------------------
ERROR: failed to build: failed to solve: process "/bin/sh -c python3 -c \"import torch, torchaudio; torch.hub.load('snakers4/silero-vad','silero_vad',trust_repo=True); print('Silero cached')\"" did not complete successfully: exit code: 1
