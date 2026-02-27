(nemo) PS C:\Users\re_nikitav\Documents\nemotron_silero> python .\client.py
🎙️ Speak now... Ctrl+C to stop
Exception ignored from cffi callback <function _StreamBase.__init__.<locals>.callback_ptr at 0x000001BB0AB2F100>:
Traceback (most recent call last):
  File "C:\Users\re_nikitav\Documents\nemotron_silero\nemo\Lib\site-packages\sounddevice.py", line 862, in callback_ptr
    return _wrap_callback(callback, data, frames, time, status)
  File "C:\Users\re_nikitav\Documents\nemotron_silero\nemo\Lib\site-packages\sounddevice.py", line 2777, in _wrap_callback
    callback(*args)
  File "C:\Users\re_nikitav\Documents\nemotron_silero\client.py", line 50, in callback
    asyncio.get_event_loop().call_soon_threadsafe(
  File "C:\Program Files\Python313\Lib\asyncio\events.py", line 716, in get_event_loop
    raise RuntimeError('There is no current event loop in thread %r.'
RuntimeError: There is no current event loop in thread 'Dummy-1'.

