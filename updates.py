getting this 

(base) root@EC03-E01-AICOE1:/home/CORP/re_nikitav# kubectl logs -f  deployment/asr-realtime-custom-vad -n cx-speech
INFO:     Started server process [1]
INFO:     Waiting for application startup.
2026-03-11 10:59:50,509 - INFO - Preloading ASR engines...
2026-03-11 10:59:50,614 - INFO - HTTP Request: HEAD https://huggingface.co/openai/whisper-large-v3-turbo/resolve/main/processor_config.json "HTTP/1.1 404 Not Found"
2026-03-11 10:59:50,643 - INFO - HTTP Request: HEAD https://huggingface.co/openai/whisper-large-v3-turbo/resolve/main/preprocessor_config.json "HTTP/1.1 307 Temporary Redirect"
2026-03-11 10:59:50,657 - INFO - HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/openai/whisper-large-v3-turbo/41f01f3fe87f28c78e2fbf8b568835947dd65ed9/preprocessor_config.json "HTTP/1.1 200 OK"
2026-03-11 10:59:50,672 - INFO - HTTP Request: GET https://huggingface.co/api/resolve-cache/models/openai/whisper-large-v3-turbo/41f01f3fe87f28c78e2fbf8b568835947dd65ed9/preprocessor_config.json "HTTP/1.1 200 OK"
2026-03-11 10:59:50,704 - INFO - HTTP Request: HEAD https://huggingface.co/openai/whisper-large-v3-turbo/resolve/main/processor_config.json "HTTP/1.1 404 Not Found"
2026-03-11 10:59:50,733 - INFO - HTTP Request: HEAD https://huggingface.co/openai/whisper-large-v3-turbo/resolve/main/preprocessor_config.json "HTTP/1.1 307 Temporary Redirect"
2026-03-11 10:59:50,746 - INFO - HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/openai/whisper-large-v3-turbo/41f01f3fe87f28c78e2fbf8b568835947dd65ed9/preprocessor_config.json "HTTP/1.1 200 OK"
2026-03-11 10:59:50,780 - INFO - HTTP Request: GET https://huggingface.co/api/models/openai/whisper-large-v3-turbo/tree/main/additional_chat_templates?recursive=false&expand=false "HTTP/1.1 404 Not Found"
2026-03-11 10:59:50,812 - INFO - HTTP Request: HEAD https://huggingface.co/openai/whisper-large-v3-turbo/resolve/main/processor_config.json "HTTP/1.1 404 Not Found"
2026-03-11 10:59:50,844 - INFO - HTTP Request: HEAD https://huggingface.co/openai/whisper-large-v3-turbo/resolve/main/chat_template.json "HTTP/1.1 404 Not Found"
2026-03-11 10:59:50,872 - INFO - HTTP Request: HEAD https://huggingface.co/openai/whisper-large-v3-turbo/resolve/main/chat_template.jinja "HTTP/1.1 404 Not Found"
2026-03-11 10:59:50,901 - INFO - HTTP Request: HEAD https://huggingface.co/openai/whisper-large-v3-turbo/resolve/main/audio_tokenizer_config.json "HTTP/1.1 404 Not Found"
2026-03-11 10:59:50,933 - INFO - HTTP Request: HEAD https://huggingface.co/openai/whisper-large-v3-turbo/resolve/main/processor_config.json "HTTP/1.1 404 Not Found"
2026-03-11 10:59:50,967 - INFO - HTTP Request: HEAD https://huggingface.co/openai/whisper-large-v3-turbo/resolve/main/preprocessor_config.json "HTTP/1.1 307 Temporary Redirect"
2026-03-11 10:59:50,981 - INFO - HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/openai/whisper-large-v3-turbo/41f01f3fe87f28c78e2fbf8b568835947dd65ed9/preprocessor_config.json "HTTP/1.1 200 OK"
2026-03-11 10:59:51,019 - INFO - HTTP Request: HEAD https://huggingface.co/openai/whisper-large-v3-turbo/resolve/main/processor_config.json "HTTP/1.1 404 Not Found"
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
2026-03-11 10:59:51,019 - WARNING - Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
2026-03-11 10:59:51,049 - INFO - HTTP Request: HEAD https://huggingface.co/openai/whisper-large-v3-turbo/resolve/main/preprocessor_config.json "HTTP/1.1 307 Temporary Redirect"
2026-03-11 10:59:51,063 - INFO - HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/openai/whisper-large-v3-turbo/41f01f3fe87f28c78e2fbf8b568835947dd65ed9/preprocessor_config.json "HTTP/1.1 200 OK"
2026-03-11 10:59:51,092 - INFO - HTTP Request: HEAD https://huggingface.co/openai/whisper-large-v3-turbo/resolve/main/config.json "HTTP/1.1 307 Temporary Redirect"
2026-03-11 10:59:51,106 - INFO - HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/openai/whisper-large-v3-turbo/41f01f3fe87f28c78e2fbf8b568835947dd65ed9/config.json "HTTP/1.1 200 OK"
2026-03-11 10:59:51,120 - INFO - HTTP Request: GET https://huggingface.co/api/resolve-cache/models/openai/whisper-large-v3-turbo/41f01f3fe87f28c78e2fbf8b568835947dd65ed9/config.json "HTTP/1.1 200 OK"
2026-03-11 10:59:51,158 - INFO - HTTP Request: HEAD https://huggingface.co/openai/whisper-large-v3-turbo/resolve/main/tokenizer_config.json "HTTP/1.1 307 Temporary Redirect"
2026-03-11 10:59:51,172 - INFO - HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/openai/whisper-large-v3-turbo/41f01f3fe87f28c78e2fbf8b568835947dd65ed9/tokenizer_config.json "HTTP/1.1 200 OK"
2026-03-11 10:59:51,186 - INFO - HTTP Request: GET https://huggingface.co/api/resolve-cache/models/openai/whisper-large-v3-turbo/41f01f3fe87f28c78e2fbf8b568835947dd65ed9/tokenizer_config.json "HTTP/1.1 200 OK"
2026-03-11 10:59:51,225 - INFO - HTTP Request: GET https://huggingface.co/api/models/openai/whisper-large-v3-turbo/tree/main/additional_chat_templates?recursive=false&expand=false "HTTP/1.1 404 Not Found"
2026-03-11 10:59:51,258 - INFO - HTTP Request: GET https://huggingface.co/api/models/openai/whisper-large-v3-turbo/tree/main?recursive=true&expand=false "HTTP/1.1 200 OK"
2026-03-11 10:59:51,288 - INFO - HTTP Request: HEAD https://huggingface.co/openai/whisper-large-v3-turbo/resolve/main/vocab.json "HTTP/1.1 307 Temporary Redirect"
2026-03-11 10:59:51,301 - INFO - HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/openai/whisper-large-v3-turbo/41f01f3fe87f28c78e2fbf8b568835947dd65ed9/vocab.json "HTTP/1.1 200 OK"
2026-03-11 10:59:51,316 - INFO - HTTP Request: GET https://huggingface.co/api/resolve-cache/models/openai/whisper-large-v3-turbo/41f01f3fe87f28c78e2fbf8b568835947dd65ed9/vocab.json "HTTP/1.1 200 OK"
2026-03-11 10:59:51,397 - INFO - HTTP Request: HEAD https://huggingface.co/openai/whisper-large-v3-turbo/resolve/main/tokenizer.json "HTTP/1.1 307 Temporary Redirect"
2026-03-11 10:59:51,421 - INFO - HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/openai/whisper-large-v3-turbo/41f01f3fe87f28c78e2fbf8b568835947dd65ed9/tokenizer.json "HTTP/1.1 200 OK"
2026-03-11 10:59:51,435 - INFO - HTTP Request: GET https://huggingface.co/api/resolve-cache/models/openai/whisper-large-v3-turbo/41f01f3fe87f28c78e2fbf8b568835947dd65ed9/tokenizer.json "HTTP/1.1 200 OK"
2026-03-11 10:59:51,486 - INFO - HTTP Request: HEAD https://huggingface.co/openai/whisper-large-v3-turbo/resolve/main/merges.txt "HTTP/1.1 307 Temporary Redirect"
2026-03-11 10:59:51,500 - INFO - HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/openai/whisper-large-v3-turbo/41f01f3fe87f28c78e2fbf8b568835947dd65ed9/merges.txt "HTTP/1.1 200 OK"
2026-03-11 10:59:51,514 - INFO - HTTP Request: GET https://huggingface.co/api/resolve-cache/models/openai/whisper-large-v3-turbo/41f01f3fe87f28c78e2fbf8b568835947dd65ed9/merges.txt "HTTP/1.1 200 OK"
2026-03-11 10:59:51,547 - INFO - HTTP Request: HEAD https://huggingface.co/openai/whisper-large-v3-turbo/resolve/main/normalizer.json "HTTP/1.1 307 Temporary Redirect"
2026-03-11 10:59:51,561 - INFO - HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/openai/whisper-large-v3-turbo/41f01f3fe87f28c78e2fbf8b568835947dd65ed9/normalizer.json "HTTP/1.1 200 OK"
2026-03-11 10:59:51,577 - INFO - HTTP Request: GET https://huggingface.co/api/resolve-cache/models/openai/whisper-large-v3-turbo/41f01f3fe87f28c78e2fbf8b568835947dd65ed9/normalizer.json "HTTP/1.1 200 OK"
2026-03-11 10:59:51,610 - INFO - HTTP Request: HEAD https://huggingface.co/openai/whisper-large-v3-turbo/resolve/main/added_tokens.json "HTTP/1.1 307 Temporary Redirect"
2026-03-11 10:59:51,624 - INFO - HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/openai/whisper-large-v3-turbo/41f01f3fe87f28c78e2fbf8b568835947dd65ed9/added_tokens.json "HTTP/1.1 200 OK"
2026-03-11 10:59:51,638 - INFO - HTTP Request: GET https://huggingface.co/api/resolve-cache/models/openai/whisper-large-v3-turbo/41f01f3fe87f28c78e2fbf8b568835947dd65ed9/added_tokens.json "HTTP/1.1 200 OK"
2026-03-11 10:59:51,669 - INFO - HTTP Request: HEAD https://huggingface.co/openai/whisper-large-v3-turbo/resolve/main/special_tokens_map.json "HTTP/1.1 307 Temporary Redirect"
2026-03-11 10:59:51,683 - INFO - HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/openai/whisper-large-v3-turbo/41f01f3fe87f28c78e2fbf8b568835947dd65ed9/special_tokens_map.json "HTTP/1.1 200 OK"
2026-03-11 10:59:51,697 - INFO - HTTP Request: GET https://huggingface.co/api/resolve-cache/models/openai/whisper-large-v3-turbo/41f01f3fe87f28c78e2fbf8b568835947dd65ed9/special_tokens_map.json "HTTP/1.1 200 OK"
2026-03-11 10:59:52,229 - INFO - HTTP Request: HEAD https://huggingface.co/openai/whisper-large-v3-turbo/resolve/main/config.json "HTTP/1.1 307 Temporary Redirect"
2026-03-11 10:59:52,243 - INFO - HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/openai/whisper-large-v3-turbo/41f01f3fe87f28c78e2fbf8b568835947dd65ed9/config.json "HTTP/1.1 200 OK"
`torch_dtype` is deprecated! Use `dtype` instead!
2026-03-11 10:59:52,306 - INFO - HTTP Request: HEAD https://huggingface.co/openai/whisper-large-v3-turbo/resolve/main/model.safetensors "HTTP/1.1 302 Found"
2026-03-11 10:59:52,366 - INFO - HTTP Request: GET https://huggingface.co/api/models/openai/whisper-large-v3-turbo/xet-read-token/41f01f3fe87f28c78e2fbf8b568835947dd65ed9 "HTTP/1.1 200 OK"
DEBUG: Startup cfg.model_name='nemotron-speech-streaming-en-0.6b.nemo' cfg.asr_backend='nemotron'
Loading whisper (openai/whisper-large-v3-turbo)...
Loading weights: 100%|██████████| 587/587 [00:00<00:00, 2658.79it/s]
2026-03-11 11:00:21,123 - INFO - HTTP Request: HEAD https://huggingface.co/openai/whisper-large-v3-turbo/resolve/main/generation_config.json "HTTP/1.1 307 Temporary Redirect"
2026-03-11 11:00:21,138 - INFO - HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/openai/whisper-large-v3-turbo/41f01f3fe87f28c78e2fbf8b568835947dd65ed9/generation_config.json "HTTP/1.1 200 OK"
2026-03-11 11:00:21,155 - INFO - HTTP Request: GET https://huggingface.co/api/resolve-cache/models/openai/whisper-large-v3-turbo/41f01f3fe87f28c78e2fbf8b568835947dd65ed9/generation_config.json "HTTP/1.1 200 OK"
2026-03-11 11:00:21,204 - ERROR - Failed to preload whisper: Found no NVIDIA driver on your system. Please check that you have an NVIDIA GPU and installed a driver from http://www.nvidia.com/Download/index.aspx
2026-03-11 11:00:22,234 - INFO - generated new fontManager
[NeMo W 2026-03-11 11:00:23 nemo_logging:405] /usr/local/lib/python3.11/site-packages/pydub/utils.py:170: RuntimeWarning: Couldn't find ffmpeg or avconv - defaulting to ffmpeg, but may not work
      warn("Couldn't find ffmpeg or avconv - defaulting to ffmpeg, but may not work", RuntimeWarning)

Loading nemotron (nemotron-speech-streaming-en-0.6b.nemo)...
[NeMo I 2026-03-11 11:00:36 nemo_logging:393] Tokenizer SentencePieceTokenizer initialized with 1024 tokens
[NeMo W 2026-03-11 11:00:37 nemo_logging:405] If you intend to do training or fine-tuning, please call the ModelPT.setup_training_data() method and provide a valid configuration file to setup the train data loader.
    Train config :
    use_lhotse: true
    skip_missing_manifest_entries: true
    input_cfg: null
    tarred_audio_filepaths: null
    manifest_filepath: null
    sample_rate: 16000
    shuffle: true
    num_workers: 2
    pin_memory: true
    max_duration: 40.0
    min_duration: 0.1
    text_field: answer
    batch_duration: null
    use_bucketing: true
    max_tps: null
    bucket_duration_bins: null
    bucket_batch_size: null
    num_buckets: null
    bucket_buffer_size: null
    shuffle_buffer_size: null
    augmentor: null

[NeMo W 2026-03-11 11:00:37 nemo_logging:405] If you intend to do validation, please call the ModelPT.setup_validation_data() or ModelPT.setup_multiple_validation_data() method and provide a valid configuration file to setup the validation data loader(s).
    Validation config :
    use_lhotse: true
    manifest_filepath: /data/ASR/en/librispeech/test-other.json
    sample_rate: 16000
    batch_size: 32
    shuffle: false
    max_duration: 40.0
    min_duration: 0.1
    num_workers: 2
    pin_memory: true
    text_field: answer
    tarred_audio_filepaths: null

[NeMo I 2026-03-11 11:00:37 nemo_logging:393] PADDING: 0
[NeMo I 2026-03-11 11:00:40 nemo_logging:393] Using RNNT Loss : warprnnt_numba
    Loss warprnnt_numba_kwargs: {'fastemit_lambda': 0.005, 'clamp': -1.0}
[NeMo I 2026-03-11 11:00:40 nemo_logging:393] Using RNNT Loss : warprnnt_numba
    Loss warprnnt_numba_kwargs: {'fastemit_lambda': 0.005, 'clamp': -1.0}
[NeMo W 2026-03-11 11:00:40 nemo_logging:405] No conditional node support for Cuda.
    Cuda graphs with while loops are disabled, decoding speed will be slower
    Reason: CUDA is not available
[NeMo I 2026-03-11 11:00:40 nemo_logging:393] Using RNNT Loss : warprnnt_numba
    Loss warprnnt_numba_kwargs: {'fastemit_lambda': 0.005, 'clamp': -1.0}
[NeMo W 2026-03-11 11:00:40 nemo_logging:405] No conditional node support for Cuda.
    Cuda graphs with while loops are disabled, decoding speed will be slower
    Reason: CUDA is not available
[NeMo I 2026-03-11 11:00:42 nemo_logging:393] Model EncDecRNNTBPEModel was successfully restored from /srv/nemotron-speech-streaming-en-0.6b.nemo.
2026-03-11 11:00:42,676 - ERROR - Failed to preload nemotron: Found no NVIDIA driver on your system. Please check that you have an NVIDIA GPU and installed a driver from http://www.nvidia.com/Download/index.aspx
2026-03-11 11:00:42,809 - INFO - Preloaded google in 0.13s
2026-03-11 11:00:42,809 - INFO - All engines preloaded.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8002 (Press CTRL+C to quit)
Loading google (google-stt-v2-streaming)...
INFO:     10.90.114.241:29092 - "GET / HTTP/1.1" 404 Not Found
INFO:     10.90.114.89:47356 - "GET / HTTP/1.1" 404 Not Found
INFO:     10.90.114.241:9846 - "GET / HTTP/1.1" 404 Not Found
INFO:     10.90.114.89:38462 - "GET / HTTP/1.1" 404 Not Found
INFO:     10.90.114.241:17858 - "GET / HTTP/1.1" 404 Not Found
INFO:     10.90.114.89:16702 - "GET / HTTP/1.1" 404 Not Found
INFO:     10.90.114.241:9180 - "GET / HTTP/1.1" 404 Not Found
INFO:     10.90.114.89:10860 - "GET / HTTP/1.1" 404 Not Found
INFO:     10.90.114.241:58492 - "GET / HTTP/1.1" 404 Not Found
INFO:     10.90.114.89:23324 - "GET / HTTP/1.1" 404 Not Found
INFO:     10.90.114.241:52360 - "GET / HTTP/1.1" 404 Not Found
INFO:     10.90.114.89:12360 - "GET / HTTP/1.1" 404 Not Found
INFO:     10.90.114.241:51962 - "GET / HTTP/1.1" 404 Not Found
INFO:     10.90.114.89:35116 - "GET / HTTP/1.1" 404 Not Found
INFO:     10.90.114.241:3060 - "GET / HTTP/1.1" 404 Not Found
INFO:     10.90.114.89:57998 - "GET / HTTP/1.1" 404 Not Found
INFO:     10.90.114.241:54972 - "GET / HTTP/1.1" 404 Not Found
INFO:     10.90.114.89:16964 - "GET / HTTP/1.1" 404 Not Found
INFO:     10.90.114.241:44102 - "GET / HTTP/1.1" 404 Not Found
INFO:     10.90.114.89:34696 - "GET / HTTP/1.1" 404 Not Found

