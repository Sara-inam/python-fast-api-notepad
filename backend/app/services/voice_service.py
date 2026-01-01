from vosk import Model, KaldiRecognizer
import sounddevice as sd
import asyncio
import json
import queue
import threading

audio_q = queue.Queue()
clients = []

# Load Vosk model
model = Model("app/vosk-model/vosk-model-small-en-us-0.15")
loop = asyncio.get_event_loop()

def get_input_device():
    """Try to get mic device, return None if not found"""
    for idx, dev in enumerate(sd.query_devices()):
        if dev['max_input_channels'] > 0:
            return idx
    return None  # no mic found

def start_voice_to_text_stream():
    rec = KaldiRecognizer(model, 16000)
    device_index = get_input_device()

    if device_index is None:
        print(" No microphone detected! Voice-to-text disabled until mic is connected.")
        return  # stop thread safely, server won't crash

    def callback(indata, frames, time, status):
        audio_q.put(bytes(indata))

    print(f"Using input device: {device_index}")
    try:
        with sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=callback,
            device=device_index,
        ):
            while True:
                data = audio_q.get()
                if rec.AcceptWaveform(data):
                    text = json.loads(rec.Result()).get("text", "")
                    if text:
                        # Send text to all clients
                        for client in clients:
                            asyncio.run_coroutine_threadsafe(
                                client.send_text(text), loop
                            )
    except Exception as e:
        print(f" Microphone stream error: {e}")
        # Do not crash server, just stop stream safely

# Start thread safely
threading.Thread(target=start_voice_to_text_stream, daemon=True).start()
