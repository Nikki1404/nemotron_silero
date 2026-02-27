      pruning_mode: LATE
      allow_cuda_graphs: true
      tsd_max_sym_exp: 50
    temperature: 1.0
    durations: []
    big_blank_durations: []

[INIT] Warming up model...
Traceback (most recent call last):
  File "/usr/local/bin/uvicorn", line 6, in <module>
    sys.exit(main())
  File "/usr/local/lib/python3.10/dist-packages/click/core.py", line 1485, in __call__
    return self.main(*args, **kwargs)
  File "/usr/local/lib/python3.10/dist-packages/click/core.py", line 1406, in main
    rv = self.invoke(ctx)
  File "/usr/local/lib/python3.10/dist-packages/click/core.py", line 1269, in invoke
    return ctx.invoke(self.callback, **ctx.params)
  File "/usr/local/lib/python3.10/dist-packages/click/core.py", line 824, in invoke
    return callback(*args, **kwargs)
  File "/usr/local/lib/python3.10/dist-packages/uvicorn/main.py", line 433, in main
    run(
  File "/usr/local/lib/python3.10/dist-packages/uvicorn/main.py", line 606, in run
    server.run()
  File "/usr/local/lib/python3.10/dist-packages/uvicorn/server.py", line 75, in run
    return asyncio_run(self.serve(sockets=sockets), loop_factory=self.config.get_loop_factory())
  File "/usr/local/lib/python3.10/dist-packages/uvicorn/_compat.py", line 60, in asyncio_run
    return loop.run_until_complete(main)
  File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
  File "/usr/local/lib/python3.10/dist-packages/uvicorn/server.py", line 79, in serve
    await self._serve(sockets)
  File "/usr/local/lib/python3.10/dist-packages/uvicorn/server.py", line 86, in _serve
    config.load()
  File "/usr/local/lib/python3.10/dist-packages/uvicorn/config.py", line 441, in load
    self.loaded_app = import_from_string(self.app)
  File "/usr/local/lib/python3.10/dist-packages/uvicorn/importer.py", line 19, in import_from_string
    module = importlib.import_module(module_str)
  File "/usr/lib/python3.10/importlib/__init__.py", line 126, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
  File "<frozen importlib._bootstrap>", line 1050, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1027, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1006, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 688, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 883, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "/app/server.py", line 180, in <module>
    asr = NemotronStreamer()
  File "/app/server.py", line 98, in __init__
    self.stream_step(dummy)
  File "/app/server.py", line 116, in stream_step
    processed_signal, processed_signal_length = self.preprocessor(audio_signal, audio_len)
  File "/usr/local/lib/python3.10/dist-packages/torch/nn/modules/module.py", line 1736, in _wrapped_call_impl
    return self._call_impl(*args, **kwargs)
  File "/usr/local/lib/python3.10/dist-packages/torch/nn/modules/module.py", line 1747, in _call_impl
    return forward_call(*args, **kwargs)
  File "/usr/local/lib/python3.10/dist-packages/nemo/core/classes/common.py", line 1192, in wrapped_call
    raise TypeError("All arguments must be passed by kwargs only for typed methods")
TypeError: All arguments must be passed by kwargs only for typed methods
(base) root@EC03-E01-AICOE1:/home/CORP/re_nikitav/nemotron_silero#
                                                      getting this while docker run now 
