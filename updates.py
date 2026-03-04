(nemo_env) root@EC03-E01-AICOE1:/home/CORP/re_nikitav/nemotron_silero/benchmarking# python benchmarking.py
  0%|                                                                                                         | 0/15 [00:00<?, ?it/s]Connecting to Silero: ws://127.0.0.1:8082/ws
Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0000/ proxy rejected connection: HTTP 400
  7%|██████▍                                                                                          | 1/15 [00:00<00:04,  3.47it/s]Connecting to Silero: ws://127.0.0.1:8082/ws
Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0001/ proxy rejected connection: HTTP 400
 13%|████████████▉                                                                                    | 2/15 [00:00<00:02,  4.36it/s]Connecting to Silero: ws://127.0.0.1:8082/ws
Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0002/ proxy rejected connection: HTTP 400
 20%|███████████████████▍                                                                             | 3/15 [00:00<00:02,  4.52it/s]Connecting to Silero: ws://127.0.0.1:8082/ws
Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0003/ proxy rejected connection: HTTP 400
 27%|█████████████████████████▊                                                                       | 4/15 [00:00<00:02,  4.71it/s]Connecting to Silero: ws://127.0.0.1:8082/ws
Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0004/ proxy rejected connection: HTTP 400
 33%|████████████████████████████████▎                                                                | 5/15 [00:01<00:02,  4.59it/s]Connecting to Silero: ws://127.0.0.1:8082/ws
Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0005/ proxy rejected connection: HTTP 400
 40%|██████████████████████████████████████▊                                                          | 6/15 [00:01<00:01,  4.62it/s]Connecting to Silero: ws://127.0.0.1:8082/ws
Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0006/ proxy rejected connection: HTTP 400
 47%|█████████████████████████████████████████████▎                                                   | 7/15 [00:01<00:01,  4.65it/s]Connecting to Silero: ws://127.0.0.1:8082/ws
Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0007/ proxy rejected connection: HTTP 400
 53%|███████████████████████████████████████████████████▋                                             | 8/15 [00:01<00:01,  4.64it/s]Connecting to Silero: ws://127.0.0.1:8082/ws
Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0008/ proxy rejected connection: HTTP 400
 60%|██████████████████████████████████████████████████████████▏                                      | 9/15 [00:01<00:01,  4.60it/s]Connecting to Silero: ws://127.0.0.1:8082/ws
Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0009/ proxy rejected connection: HTTP 400
 67%|████████████████████████████████████████████████████████████████                                | 10/15 [00:02<00:01,  4.44it/s]Connecting to Silero: ws://127.0.0.1:8082/ws
Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0010/ proxy rejected connection: HTTP 400
 73%|██████████████████████████████████████████████████████████████████████▍                         | 11/15 [00:02<00:00,  4.56it/s]Connecting to Silero: ws://127.0.0.1:8082/ws
Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0011/ proxy rejected connection: HTTP 400
 80%|████████████████████████████████████████████████████████████████████████████▊                   | 12/15 [00:02<00:00,  4.55it/s]Connecting to Silero: ws://127.0.0.1:8082/ws
Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0012/ proxy rejected connection: HTTP 400
 87%|███████████████████████████████████████████████████████████████████████████████████▏            | 13/15 [00:02<00:00,  4.76it/s]Connecting to Silero: ws://127.0.0.1:8082/ws
Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0013/ proxy rejected connection: HTTP 400
 93%|█████████████████████████████████████████████████████████████████████████████████████████▌      | 14/15 [00:03<00:00,  4.61it/s]Connecting to Silero: ws://127.0.0.1:8082/ws
Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0014/ proxy rejected connection: HTTP 400
100%|████████████████████████████████████████████████████████████████████████████████████████████████| 15/15 [00:03<00:00,  4.63it/s]
Traceback (most recent call last):
  File "/home/CORP/re_nikitav/nemotron_silero/benchmarking/benchmarking.py", line 317, in <module>
    asyncio.run(main())
  File "/usr/lib/python3.10/asyncio/runners.py", line 44, in run
    return loop.run_until_complete(main)
  File "/usr/lib/python3.10/asyncio/base_events.py", line 649, in run_until_complete
    return future.result()
  File "/home/CORP/re_nikitav/nemotron_silero/benchmarking/benchmarking.py", line 313, in main
    write_to_file(results)
  File "/home/CORP/re_nikitav/nemotron_silero/benchmarking/benchmarking.py", line 275, in write_to_file
    df = df[[
  File "/home/CORP/re_nikitav/nemotron_silero/benchmarking/nemo_env/lib/python3.10/site-packages/pandas/core/frame.py", line 4119, in __getitem__
    indexer = self.columns._get_indexer_strict(key, "columns")[1]
  File "/home/CORP/re_nikitav/nemotron_silero/benchmarking/nemo_env/lib/python3.10/site-packages/pandas/core/indexes/base.py", line 6212, in _get_indexer_strict
    self._raise_if_missing(keyarr, indexer, axis_name)
  File "/home/CORP/re_nikitav/nemotron_silero/benchmarking/nemo_env/lib/python3.10/site-packages/pandas/core/indexes/base.py", line 6261, in _raise_if_missing
    raise KeyError(f"None of [{key}] are in the [{axis_name}]")
KeyError: "None of [Index(['filename', 'silero-ttfb(ms)', 'custom-vad-ttfb(ms)', 'silero-wer',\n       'custom-vad-wer', 'reference-text', 'silero-text', 'custom-vad-text',\n       'normalized-silero-wer', 'normalized-custom-vad-wer',\n       'normalized-reference-text', 'normalized-sielro-text',\n       'normalized-custom-vad-text'],\n      dtype='object')] are in the [columns]"

getting this error 
