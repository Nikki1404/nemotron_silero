after first file in custom vad server logs getting this 

2026-03-04 19:15:18,053 - INFO -  Preloaded nemotron (nvidia/nemotron-speech-streaming-en-0.6b) in 91.72s
   Loading google (google-stt-v2-streaming)...
2026-03-04 19:15:18,217 - INFO -  Preloaded google (google-stt-v2-streaming) in 0.16s
2026-03-04 19:15:18,217 - INFO -  All engines preloaded! Client requests will be INSTANT.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8002 (Press CTRL+C to quit)
INFO:     172.17.0.1:54692 - "WebSocket /asr/realtime-custom-vad" [accepted]
INFO:     connection open
2026-03-04 19:36:45,033 - INFO -  Using cached nemotron engine (0ms latency!)
2026-03-04 19:36:45,034 - INFO - WS connected (nemotron) Address(host='172.17.0.1', port=54692)
2026-03-04 19:36:46,285 - INFO - CLIENT: Address(host='172.17.0.1', port=54692), TEXT: L, START_TIME : 1772653005596
2026-03-04 19:36:46,443 - INFO - CLIENT: Address(host='172.17.0.1', port=54692), TEXT: Lyn, START_TIME : 1772653005596
2026-03-04 19:36:46,603 - INFO - CLIENT: Address(host='172.17.0.1', port=54692), TEXT: Lynne, START_TIME : 1772653005596
2026-03-04 19:36:46,765 - INFO - CLIENT: Address(host='172.17.0.1', port=54692), TEXT: Lynnell, START_TIME : 1772653005596
2026-03-04 19:36:46,930 - INFO - CLIENT: Address(host='172.17.0.1', port=54692), TEXT: Lynnell's pict, START_TIME : 1772653005596
2026-03-04 19:36:47,089 - INFO - CLIENT: Address(host='172.17.0.1', port=54692), TEXT: Lynnell's pictures, START_TIME : 1772653005596
2026-03-04 19:36:47,413 - INFO - CLIENT: Address(host='172.17.0.1', port=54692), TEXT: Lynnell's pictures are, START_TIME : 1772653005596
2026-03-04 19:36:47,575 - INFO - CLIENT: Address(host='172.17.0.1', port=54692), TEXT: Lynnell's pictures are a, START_TIME : 1772653005596
2026-03-04 19:36:47,738 - INFO - CLIENT: Address(host='172.17.0.1', port=54692), TEXT: Lynnell's pictures are a sort of, START_TIME : 1772653005596
2026-03-04 19:36:48,707 - INFO - CLIENT: Address(host='172.17.0.1', port=54692), TEXT: Lynnell's pictures are a sort of up, START_TIME : 1772653005596
2026-03-04 19:36:48,866 - INFO - CLIENT: Address(host='172.17.0.1', port=54692), TEXT: Lynnell's pictures are a sort of upg, START_TIME : 1772653005596
2026-03-04 19:36:49,029 - INFO - CLIENT: Address(host='172.17.0.1', port=54692), TEXT: Lynnell's pictures are a sort of upguards, START_TIME : 1772653005596
2026-03-04 19:36:49,191 - INFO - CLIENT: Address(host='172.17.0.1', port=54692), TEXT: Lynnell's pictures are a sort of upguards and, START_TIME : 1772653005596
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "/usr/local/lib/python3.10/dist-packages/uvicorn/protocols/websockets/websockets_impl.py", line 244, in run_asgi
    result = await self.app(self.scope, self.asgi_receive, self.asgi_send)  # type: ignore[func-returns-value]
  File "/usr/local/lib/python3.10/dist-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
    return await self.app(scope, receive, send)
  File "/usr/local/lib/python3.10/dist-packages/fastapi/applications.py", line 1134, in __call__
    await super().__call__(scope, receive, send)
  File "/usr/local/lib/python3.10/dist-packages/starlette/applications.py", line 107, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.10/dist-packages/starlette/middleware/errors.py", line 151, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.10/dist-packages/starlette/middleware/exceptions.py", line 63, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.10/dist-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.10/dist-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.10/dist-packages/fastapi/middleware/asyncexitstack.py", line 18, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.10/dist-packages/starlette/routing.py", line 716, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.10/dist-packages/starlette/routing.py", line 736, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.10/dist-packages/starlette/routing.py", line 364, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.10/dist-packages/fastapi/routing.py", line 145, in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
  File "/usr/local/lib/python3.10/dist-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.10/dist-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.10/dist-packages/fastapi/routing.py", line 142, in app
    await func(session)
  File "/usr/local/lib/python3.10/dist-packages/fastapi/routing.py", line 507, in app
    await dependant.call(**solved_result.values)
  File "/srv/app/main.py", line 247, in ws_asr
    await ws.close()
  File "/usr/local/lib/python3.10/dist-packages/starlette/websockets.py", line 181, in close
    await self.send({"type": "websocket.close", "code": code, "reason": reason or ""})
  File "/usr/local/lib/python3.10/dist-packages/starlette/websockets.py", line 86, in send
    await self._send(message)
  File "/usr/local/lib/python3.10/dist-packages/starlette/_exception_handler.py", line 39, in sender
    await send(message)
  File "/usr/local/lib/python3.10/dist-packages/uvicorn/protocols/websockets/websockets_impl.py", line 357, in asgi_send
    raise RuntimeError(msg % message_type)
RuntimeError: Unexpected ASGI message 'websocket.close', after sending 'websocket.close' or response already completed.
INFO:     connection closed
INFO:     172.17.0.1:34056 - "WebSocket /asr/realtime-custom-vad" [accepted]
INFO:     connection open
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "/usr/local/lib/python3.10/dist-packages/uvicorn/protocols/websockets/websockets_impl.py", line 244, in run_asgi
    result = await self.app(self.scope, self.asgi_receive, self.asgi_send)  # type: ignore[func-returns-value]
  File "/usr/local/lib/python3.10/dist-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
    return await self.app(scope, receive, send)
  File "/usr/local/lib/python3.10/dist-packages/fastapi/applications.py", line 1134, in __call__
    await super().__call__(scope, receive, send)
  File "/usr/local/lib/python3.10/dist-packages/starlette/applications.py", line 107, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.10/dist-packages/starlette/middleware/errors.py", line 151, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.10/dist-packages/starlette/middleware/exceptions.py", line 63, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.10/dist-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.10/dist-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.10/dist-packages/fastapi/middleware/asyncexitstack.py", line 18, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.10/dist-packages/starlette/routing.py", line 716, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.10/dist-packages/starlette/routing.py", line 736, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.10/dist-packages/starlette/routing.py", line 364, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.10/dist-packages/fastapi/routing.py", line 145, in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
  File "/usr/local/lib/python3.10/dist-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.10/dist-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.10/dist-packages/fastapi/routing.py", line 142, in app
    await func(session)
  File "/usr/local/lib/python3.10/dist-packages/fastapi/routing.py", line 507, in app
    await dependant.call(**solved_result.values)
  File "/srv/app/main.py", line 86, in ws_asr
    init = await ws.receive_text()
  File "/usr/local/lib/python3.10/dist-packages/starlette/websockets.py", line 120, in receive_text
    self._raise_on_disconnect(message)
  File "/usr/local/lib/python3.10/dist-packages/starlette/websockets.py", line 114, in _raise_on_disconnect
    raise WebSocketDisconnect(message["code"], message.get("reason"))
starlette.websockets.WebSocketDisconnect: (<CloseCode.ABNORMAL_CLOSURE: 1006>, '')
INFO:     connection closed

and in benchmarking side getting this 
(nemo_env) root@EC03-E01-AICOE1:/home/CORP/re_nikitav/nemotron_silero/benchmarking# python benchmarking.py
  0%|                                                                                                         | 0/15 [00:00<?, ?it/s]Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0000/
  7%|██████▍                                                                                          | 1/15 [01:06<15:25, 66.12s/it]Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0001/
 13%|████████████▉                                                                                    | 2/15 [02:11<14:12, 65.55s/it]Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0002/
 20%|███████████████████▍                                                                             | 3/15 [03:24<13:46, 68.91s/it]Error in folder: asr-realtime/benchmarking-data-3/1272_1281041272-128104-0003/
 27%|█████████████████████████▊                                                                       | 4/15 [04:34<12:43, 69.43s/it


nemotron_silero did transcribing so there is no error in server logs 
