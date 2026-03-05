import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer
from queuem import analysis_queue
# import queue
# analysis_queue = queue.Queue()
def start_recording():
    q = queue.Queue()
    samplerate = 16000
    model = Model("vosk-model-small-en-us-0.15")
    rec = KaldiRecognizer(model, samplerate)

    def callback(indata, frames, time, status):
        q.put(bytes(indata))

    print("\n--- [SYSTEM] Fake Call Ended. Recording and analyzing environment... ---")
    
    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16', 
                           channels=1, callback=callback):
        try:
            # You might want a way to stop this, like a timer or a specific keyword
            while True: 
                data = q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result["text"]
                    if text.strip():
                        print(f"Captured: {text}")
                        analysis_queue.put(text)
        except KeyboardInterrupt:
            print("\nStopping recorder...")