from flask import Flask, render_template, request, redirect
import mysql.connector
import os
import threading

app = Flask(__name__)

status_file = "lock_status.txt"
lock_timer = None  # Global timer for auto-relock

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
    print("[AUTO-RELOCK] System re-locked after 10 seconds")

@app.route('/', methods=['GET'])
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
        print("[STATUS] Unlocked via web")

        # Cancel existing timer (if any), then start a new one
        if lock_timer and lock_timer.is_alive():
            lock_timer.cancel()

        lock_timer = threading.Timer(10.0, auto_relock)
        lock_timer.start()

    else:
        set_status("Locked")
        print("[STATUS] Manually re-locked via web")

        if lock_timer and lock_timer.is_alive():
            lock_timer.cancel()

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
