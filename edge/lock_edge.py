import serial
import socketio
import requests

# ---------- GLOBALS ---------- #
DB_HOST = "localhost"
DB_USER = "server"
DB_PASS = "server"
WEB_HOST = "http://localhost:5500"
SERIAL_PORT = "COM6"
BAUD_RATE = 9600


# ---------- SETTING UP ---------- #
# Serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
# SocketIo
sio = socketio.SimpleClient()
# Temporary UID variable
uid = None
# TEMPORARY -> HAVE A TABLE IN DATABASE FOR THIS SOON
authorized_uids = []


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
                if uid in authorized_uids:
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
    else:
        message = "LOCK\n"
    
    ser.write(message.encode())
    print(f"[SERIAL] {message} command sent to Arduino")

if __name__ == "__main__":
    sio.connect(WEB_HOST)
    try:
        main_loop()
    except KeyboardInterrupt:
        print("Gracefully shutting down...")
    finally:
        ser.close()