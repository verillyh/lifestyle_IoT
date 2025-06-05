import serial
import socketio
import requests
import paho.mqtt.client as mqtt
import threading


# ---------- GLOBALS ---------- #
WEB_HOST = "http://203.101.225.4:5500"
SERIAL_PORT = "COM7"
BAUD_RATE = 9600
MQTT_BROKER = "test.mosquitto.org"
MQTT_TOPIC = "/swe30011/lifestyle/smart_devices"

# TODO: RACE CONDITION BETWEEN THREADS FOR SIO
# TODO: SHUTDOWN MQTT ON KEYBOARDINTERRUPT

# ---------- SETTING UP ---------- #
# Serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
# SocketIo
sio = socketio.Client()
# MQTT Client
client = mqtt.Client()
# Temporary UID variable
uid = None
# TEMPORARY -> HAVE A TABLE IN DATABASE FOR THIS SOON
AUTHORIZED_UIDS = ["43705EF5", "D3C77330"]


def main_loop():
    while True:
        try:
            line = ser.readline().decode().strip()
            if line:
                print(f"[SERIAL] {line}")
            
            if line.startswith("Scanned UID:"):
                # get UID
                uid = line.split(":")[1].strip().replace(" ", "")
                print(f"[UID DETECTED] {uid}")
                
                # Build JSON data for POST request
                data = {
                    "uid": uid
                }
                
                # Append access state respectively
                if uid in AUTHORIZED_UIDS:
                    data["access"] = "Granted"
                else:
                    data["access"] = "Denied"
                
                # Post to web server
                response = requests.post(f"{WEB_HOST}/insert_log", json=data)
                print("Status code of inserting log: ", response.status_code)

            elif "ALARM TRIGGERED" in line:
                print("[ALERT] Intruder alert triggered!")

        except Exception as e:
            print(f"[ERROR] {e}")
        
        


@sio.on("unlock_door")
def unlock_door(unlock):
    message = None
    if unlock:
        message = "UNLOCK\n"
        client.publish(MQTT_TOPIC, "door unlocked")
    else:
        message = "LOCK\n"
    
    ser.write(message.encode())
    print(f"[SERIAL] {message} command sent to Arduino")

# On connect to MQTT server
def on_connect(client, userdata, flags, rc):
    print("[MQTT] Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)


# On message from MQTT server
def on_message(client, userdata, msg):
    command = msg.payload.decode().lower()
    print(f"[MQTT] Received: {command}")

    if "unlock door" in command:
        sio.emit("unlock_door")

    elif "turn off light" in command:
        # ser.write(b"LIGHT_OFF\n")
        print("[ACTION] Light turned off by MQTT")


def mqtt_thread():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, 1883, 60)
    client.loop_forever()




if __name__ == "__main__":
    try:
        sio.connect(WEB_HOST)
        # Start MQTT listener
        threading.Thread(target=mqtt_thread, daemon=True).start()
        threading.Thread(target=main_loop, daemon=True).start()
        sio.wait()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        if ser.is_open:
            ser.close()
            print("Serial port closed.")
        
