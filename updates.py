(nemo_env) root@EC03-E01-AICOE1:/home/CORP/re_nikitav/nemotron_silero/benchmarking# python benchmarking.py
  0%|                                                                                                         | 0/15 [00:00<?, ?it/s]Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0000/ [Errno 111] Connect call failed ('127.0.0.1', 8000)
  7%|██████▍                                                                                          | 1/15 [00:00<00:01,  9.31it/s]Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0001/ [Errno 111] Connect call failed ('127.0.0.1', 8000)
Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0002/ [Errno 111] Connect call failed ('127.0.0.1', 8000)
 20%|███████████████████▍                                                                             | 3/15 [00:00<00:01,  9.48it/s]Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0003/ [Errno 111] Connect call failed ('127.0.0.1', 8000)
 27%|█████████████████████████▊                                                                       | 4/15 [00:00<00:01,  8.79it/s]Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0004/ [Errno 111] Connect call failed ('127.0.0.1', 8000)
 33%|████████████████████████████████▎                                                                | 5/15 [00:00<00:01,  6.84it/s]Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0005/ [Errno 111] Connect call failed ('127.0.0.1', 8000)
 40%|██████████████████████████████████████▊                                                          | 6/15 [00:00<00:01,  7.18it/s]Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0006/ [Errno 111] Connect call failed ('127.0.0.1', 8000)
 47%|█████████████████████████████████████████████▎                                                   | 7/15 [00:00<00:01,  7.49it/s]Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0007/ [Errno 111] Connect call failed ('127.0.0.1', 8000)
 53%|███████████████████████████████████████████████████▋                                             | 8/15 [00:01<00:00,  7.81it/s]Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0008/ [Errno 111] Connect call failed ('127.0.0.1', 8000)
Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0009/ [Errno 111] Connect call failed ('127.0.0.1', 8000)
 67%|████████████████████████████████████████████████████████████████                                | 10/15 [00:01<00:00,  8.17it/s]Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0010/ [Errno 111] Connect call failed ('127.0.0.1', 8000)
 73%|██████████████████████████████████████████████████████████████████████▍                         | 11/15 [00:01<00:00,  8.47it/s]Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0011/ [Errno 111] Connect call failed ('127.0.0.1', 8000)
 80%|████████████████████████████████████████████████████████████████████████████▊                   | 12/15 [00:01<00:00,  8.80it/s]Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0012/ [Errno 111] Connect call failed ('127.0.0.1', 8000)
 87%|███████████████████████████████████████████████████████████████████████████████████▏            | 13/15 [00:01<00:00,  8.76it/s]Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0013/ [Errno 111] Connect call failed ('127.0.0.1', 8000)
Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0014/ [Errno 111] Connect call failed ('127.0.0.1', 8000)
100%|████████████████████████████████████████████████████████████████████████████████████████████████| 15/15 [00:01<00:00,  8.56it/s]
Traceback (most recent call last):
  File "/home/CORP/re_nikitav/nemotron_silero/benchmarking/benchmarking.py", line 250, in <module>
    asyncio.run(main())
  File "/usr/lib/python3.10/asyncio/runners.py", line 44, in run
    return loop.run_until_complete(main)
  File "/usr/lib/python3.10/asyncio/base_events.py", line 649, in run_until_complete
    return future.result()
  File "/home/CORP/re_nikitav/nemotron_silero/benchmarking/benchmarking.py", line 246, in main
    write_to_file(results)
  File "/home/CORP/re_nikitav/nemotron_silero/benchmarking/benchmarking.py", line 213, in write_to_file
    df = df[[
  File "/home/CORP/re_nikitav/nemotron_silero/benchmarking/nemo_env/lib/python3.10/site-packages/pandas/core/frame.py", line 4119, in __getitem__
    indexer = self.columns._get_indexer_strict(key, "columns")[1]
  File "/home/CORP/re_nikitav/nemotron_silero/benchmarking/nemo_env/lib/python3.10/site-packages/pandas/core/indexes/base.py", line 6212, in _get_indexer_strict
    self._raise_if_missing(keyarr, indexer, axis_name)
  File "/home/CORP/re_nikitav/nemotron_silero/benchmarking/nemo_env/lib/python3.10/site-packages/pandas/core/indexes/base.py", line 6261, in _raise_if_missing
    raise KeyError(f"None of [{key}] are in the [{axis_name}]")
KeyError: "None of [Index(['filename', 'silero-latency', 'custom-vad-latency', 'silero-wer',\n       'custom-vad-wer', 'reference-text', 'silero-text', 'custom-vad-text',\n       'normalized-silero-wer', 'normalized-custom-vad-wer',\n       'normalized-reference-text', 'normalized-sielro-text',\n       'normalized-custom-vad-text'],\n      dtype='object')] are in the [columns]"
(nemo_env) root@EC03-E01-AICOE1:/home/CORP/re_nikitav/nemotron_silero/benchmarking#


why getting this ?
