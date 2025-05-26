import serial
import mysql.connector
import time
import paho.mqtt.client as mqtt
import threading

# Serial port config (adjust as needed)
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="vince",
    password="vinny",
    database="smartlock"
)
cursor = db.cursor()

uid = None

def insert_log(uid, status):
    cursor.execute("INSERT INTO logs (uid, status) VALUES (%s, %s)", (uid, status))
    db.commit()
    print(f"[LOGGED] UID: {uid}, Status: {status}")
    
    # Optional: update status text file (still compatible with Flask UI)
    if status == "granted":
        set_status_file("Unlocked")
        print("[STATUS] Door unlocked by RFID")

        time.sleep(10)

        set_status_file("Locked")
        print("[STATUS] Door auto-relocked after 10 seconds")

def set_status_file(new_status):
    with open("../flask/lock_status.txt", "w") as f:
        f.write(new_status)

# MQTT Setup
MQTT_BROKER = "test.mosquitto.org"
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

# Main loop: handle serial input from Arduino
while True:
    try:
        line = ser.readline().decode().strip()
        if line:
            print(f"[SERIAL] {line}")

        if line.startswith("Scanned UID:"):
            uid = line.split(":")[1].strip().replace(" ", "")
            print(f"[UID DETECTED] {uid}")

        elif "ACCESS GRANTED" in line:
            insert_log(uid, "granted")

        elif "NO ACCESS" in line:
            insert_log(uid, "denied")

        elif "ALARM TRIGGERED" in line:
            print("[ALERT] Intruder alert triggered!")

    except Exception as e:
        print(f"[ERROR] {e}")
