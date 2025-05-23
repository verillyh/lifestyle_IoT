import serial
import mysql.connector
import time

# Serial port config (update this to match your device, e.g. /dev/ttyUSB0)
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

    # Sync with website display
    if status == "granted":
        set_status_file("Unlocked")
        print("[STATUS] Door unlocked by RFID")

        time.sleep(10)

        set_status_file("Locked")
        print("[STATUS] Door auto-relocked after 10 seconds")

def set_status_file(new_status):
    with open("lock_status.txt", "w") as f:
        f.write(new_status)

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

