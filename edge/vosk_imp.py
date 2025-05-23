from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue
import json
import os

q = queue.Queue()
model = Model(lang="en-us")
piper_model = "en_US-lessac-medium"
sample_rate = 16000

def callback(indata, frames, time, status):
    q.put(bytes(indata))

try:
    # 
    with sd.RawInputStream(device=1, channels=1, blocksize=8000, callback=callback, samplerate=sample_rate, dtype="int16"):
        # Get TTS model
        rec = KaldiRecognizer(model, sample_rate)
        print("Listening...")
        while True:
            data = q.get()
            # If a complete sentence/sound was said
            if rec.AcceptWaveform(data):
                # rec.Result() returns json, so need to preprocess it
                res = json.loads(rec.Result()).get("text")
                print(res)
                # Output said sentence as TTS
                os.system(f"echo '{res}' | piper --model {os.path.join("model", piper_model)}.onnx -c {os.path.join("model", piper_model)}.onnx.json --output_file test.wav")
                break
except KeyboardInterrupt:
    print("Exiting...")