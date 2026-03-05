from openwakeword.model import Model
import numpy as np
import sounddevice as sd
import soundfile as sf
from gtts import gTTS
import time
from recorder import start_recording
from detection import start_ai_worker
import os

os.makedirs("memory", exist_ok=True)

with open("memory/conversation_log.txt", "w", encoding="utf-8") as f:
    f.write("")
global detected
detected = False
start_ai_worker()

model_path = "chikki.tflite" 
model = Model(wakeword_models=[model_path])

print(f"Listening for 'Chikki'...")
print("DEBUG MODE: You should see the 'Vol' level change when you clap.")
def play_fakecall():
    ringtone, fs = sf.read("ringtone.wav")
    sd.play(ringtone, fs)
    sd.wait()

    text = "Hello? Are you okay? I'm tracking your location."
    tts = gTTS(text=text, lang='en')
    tts.save("fakecall.wav")
    data, fs = sf.read("fakecall.wav")
    sd.play(data,fs)
    sd.wait()


def callback(indata, frames, time, status):
    
    if status:
        print(f"\nError: {status}")

    
    audio_int16 = (indata.flatten() * 32767).astype(np.int16)  
    volume_norm = np.linalg.norm(audio_int16) / np.sqrt(len(audio_int16)) 
    prediction = model.predict(audio_int16)
    if not prediction: print("Model is returning NO DATA", end='\r')
    for word, score in prediction.items():
        print(f"Vol: {int(volume_norm):4} | Score: {score:.4f}", end='\r') 
        if score > 0.3:  
            play_fakecall()
            start_recording()
            print(f"\n[!] MATCH: {word} ({score:.2f})")
            detected = True
            raise sd.CallbackStop

with sd.InputStream(samplerate=16000, channels=1, blocksize=1280, callback=callback):
    try:
        while not detected:
            sd.sleep(100)
    except KeyboardInterrupt:
        print("\nStopped.")