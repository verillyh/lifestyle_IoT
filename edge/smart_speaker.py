from vosk import Model, KaldiRecognizer
import paho.mqtt.client as mqtt
import sounddevice as sd
import queue
import json
import os
import openmeteo_requests
import requests_cache
import serial
from retry_requests import retry
from datetime import datetime


light_commands = [
    "lights on\n",
    "lights off\n",
    "motion lights\n",
    "happy light\n",
    "sad  light\n"
    "angry light\n",
    "romantic light\n",
    "party light\n",
    "relax light\n",
    "love light\n",
    "morning light\n",
    "afternoon light\n",
    "evening light\n",
    "night light\n"
]
remote_commands = [
    "unlock door"
]

# ---------- SETUP ---------- #
# Data queue
q = queue.Queue()
# Vosk model - STT
model = Model(lang="en-us")
# Piper model - TTS
PIPER_MODEL = "en_US-lessac-medium"
# Microphone sample rate 
SAMPLE_RATE = sd.query_devices(1)["default_samplerate"]
# MQTT 
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "/swe30011/lifestyle/smart_devices"
client = mqtt.Client()
# Weather API
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)
params = {
    "latitude": -37.8140,
    "longitude": 144.9633,
    "timezone": "Australia/Sydney",
    "hourly": ["precipitation_probability", "relative_humidity_2m"],
	"current": ["temperature_2m", "apparent_temperature"],
    "forecast_days": 1
}
# Serial
ser = serial.Serial("/dev/ttyACM0", 9600) 



# TODO: MAKE THIS ASYNC
def get_weather():
    response = openmeteo.weather_api(WEATHER_API_URL, params)[0]

    # Get variables
    hour_now = datetime.now().hour
    current_resp = response.Current()
    hourly_resp = response.Hourly()
    current_temp = current_resp.Variables(0).Value()
    current_apparent_temp = current_resp.Variables(1).Value()
    forecast_precipitation = hourly_resp.Variables(0).ValuesAsNumpy()[hour_now-1:]    
    forecast_humidity = hourly_resp.Variables(1).ValuesAsNumpy()[hour_now-1:]

    # Produce text for TTS
    out_text = (
        f"Current temperature is {current_temp:.1f} degrees celsius and feels like {current_apparent_temp:.1f} degrees celsius. "
        f"There is a {max(forecast_precipitation):.0f}% chance of rain, with current relative humidity at {forecast_humidity[0]:.0f}%"
    )

    return out_text

def on_connect(client, userdata, flags, rc):
    print("Connected to broker with result code: ", str(rc))


def callback(indata, frames, time, status):
    q.put(bytes(indata))

try:
    client.on_connect = on_connect
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    with sd.RawInputStream(device=1, channels=1, blocksize=8000, callback=callback, samplerate=SAMPLE_RATE, dtype="int16"):
        # Get TTS model
        rec = KaldiRecognizer(model, SAMPLE_RATE)
        print("Listening...")
        while True:
            data = q.get()
            # If a complete sentence/sound was said
            if rec.AcceptWaveform(data):
                # rec.Result() returns json, so need to preprocess it
                command = json.loads(rec.Result()).get("text")
                print(f"Command captured: {command}")
        
                # Handle voice commands
                if command in remote_commands:
                    client.publish(MQTT_TOPIC, command)
                    print(command, " published with MQTT")
                # Handle light commands
                elif command in light_commands:
                    ser.write(command.encode())
                    print(command, " sent to Arduino")
                # Ask for weather
                elif command == "what's the weather":
                    text = get_weather()
                    os.system(f"echo '{text}' | piper --model {os.path.join('..', 'model', PIPER_MODEL)}.onnx -c {os.path.join('..', 'model', PIPER_MODEL)}.onnx.json | aplay -r 22050 -f S16_LE -t raw -")    
                elif command == "stop":
                    break

except KeyboardInterrupt:
    print("Exiting...")
finally:
    sd.stop()
    client.disconnect()