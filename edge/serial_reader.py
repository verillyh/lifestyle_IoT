import serial
import mysql.connector
import time
import paho.mqtt.client as mqtt
import threading

# Serial port config
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="vince",
    password="vinny",
    database="smartlock"
)
cursor = db.cursor()

# List of authorized UIDs
AUTHORIZED_UIDS = ["43705EF5", "D3C77330"]
uid = None

def insert_log(uid, status):
    cursor.execute("INSERT INTO logs (uid, status) VALUES (%s, %s)", (uid, status))
    db.commit()
    print(f"[LOGGED] UID: {uid}, Status: {status}")
    if status == "granted":
        set_status_file("Unlocked")
        print("[STATUS] Door unlocked by RFID")
        time.sleep(10)
        set_status_file("Locked")
        print("[STATUS] Door auto-relocked after 10 seconds")

def set_status_file(new_status):
    with open("../flask/lock_status.txt", "w") as f:
        f.write(new_status)

def is_authorized(uid):
    return uid in AUTHORIZED_UIDS

# MQTT Setup
MQTT_BROKER = "test.mosquitto.org"  # Or redirected to your VM IP via /etc/hosts
MQTT_TOPIC = "/swe30011/lifestyle/smart_devices"

def on_connect(client, userdata, flags, rc):
    print("[MQTT] Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    command = msg.payload.decode().lower()
    print(f"[MQTT] Received: {command}")

    if "unlock door" in command:
        ser.write(b"UNLOCK\n")
        set_status_file("Unlocked")
        print("[ACTION] Door unlocked by MQTT")
        time.sleep(10)
        ser.write(b"LOCK\n")
        set_status_file("Locked")
        print("[AUTO-RELOCK] Door re-locked after 10 sec")

    elif "lock door" in command:
        ser.write(b"LOCK\n")
        set_status_file("Locked")
        print("[ACTION] Door locked by MQTT")

    elif "turn off light" in command:
        ser.write(b"LIGHT_OFF\n")
        print("[ACTION] Light turned off by MQTT")

def mqtt_thread():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, 1883, 60)
    client.loop_forever()

# Start MQTT listener
threading.Thread(target=mqtt_thread, daemon=True).start()

# Main loop: handle serial input
while True:
    try:
        line = ser.readline().decode().strip()
        if line:
            print(f"[SERIAL] {line}")

        if line.startswith("Scanned UID:"):
            uid = line.split(":")[1].strip().replace(" ", "")
            print(f"[UID DETECTED] {uid}")

            result = "granted" if is_authorized(uid) else "denied"
            print(f"[AUTH RESULT] {result.upper()}")
            insert_log(uid, result)

            if result == "granted":
                ser.write(b"ACCESS GRANTED\n")
            else:
                ser.write(b"NO ACCESS\n")

        elif "ALARM TRIGGERED" in line:
            print("[ALERT] Intruder alert triggered!")

    except Exception as e:
        print(f"[ERROR] {e}")

