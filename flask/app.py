from flask import Flask, render_template, request, redirect
import mysql.connector
import os
import threading
import serial

app = Flask(__name__)
status_file = "lock_status.txt"
lock_timer = None

# Setup serial connection to Arduino
try:
    arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
except:
    arduino = None
    print("[WARNING] Arduino not connected")

def get_status():
    if not os.path.exists(status_file):
        return "Locked"
    with open(status_file, "r") as f:
        return f.read().strip()

def set_status(new_status):
    with open(status_file, "w") as f:
        f.write(new_status)

def auto_relock():
    set_status("Locked")
    send_to_arduino("LOCK\n")
    print("[AUTO-RELOCK] System re-locked after 10 seconds")

def send_to_arduino(message):
    if arduino and arduino.isOpen():
        arduino.write(message.encode())
        print(f"[SERIAL] Sent to Arduino: {message.strip()}")

@app.route('/')
def index():
    conn = mysql.connector.connect(
        host="localhost",
        user="vince",
        password="vinny",
        database="smartlock"
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 10")
    logs = cursor.fetchall()
    conn.close()
    return render_template('index.html', logs=logs, status=get_status())

@app.route('/toggle', methods=['POST'])
def toggle():
    global lock_timer
    current = get_status()

    if current == "Locked":
        set_status("Unlocked")
        send_to_arduino("UNLOCK\n")

        if lock_timer and lock_timer.is_alive():
            lock_timer.cancel()
        lock_timer = threading.Timer(10.0, auto_relock)
        lock_timer.start()
    else:
        set_status("Locked")
        send_to_arduino("LOCK\n")

        if lock_timer and lock_timer.is_alive():
            lock_timer.cancel()

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
