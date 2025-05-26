import eventlet
print("Running monkey patch...")
# Eventlet
eventlet.monkey_patch()


from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
import database


# ----------- GLOBALS ----------- #
DB_HOST = "localhost"
DB_USER = "server"
DB_PASS = "server"

# ---------- SETTING UP ---------- #
print("Setting up Flask...")
# Flask app
app = Flask(__name__)
CORS(app)
app.config["SECRET_KEY"] = "secret!"
# Socket.io 
print("Setting up socket.io...")
sio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")
door_unlocked = False
db, cursor = database.connect(DB_HOST, DB_USER, DB_PASS)
print("Setup complete")

def serialize_logs(logs):
    logs_serialized = []

    for row in logs:
        row_copy = dict(row)
        row_copy["timestamp"] = row_copy['timestamp'].isoformat()
        logs_serialized.append(row_copy)
    
    return logs_serialized

@app.route('/logs')
def index():
    # TODO: FIX THIS
    global db, cursor
    cursor.execute("SELECT * FROM lock_logs ORDER BY timestamp DESC LIMIT 10")
    logs = cursor.fetchall()
    serialized = serialize_logs(logs)
    print("RETRIEVING LOGS...")
    print(serialized)
    return jsonify(logs=serialized)

@app.route("/insert_log", methods=["POST"])
def insert_log():
    data = request.get_json()
    
    uid = data.get("uid")
    access = data.get("access")
    try:
        cursor.execute("""
            INSERT INTO lock_logs(uid, status) VALUES(%s, %s)
        """, (uid, access))
        db.commit()
    except Exception as e:
        print("Error inserting into log: ", e)

@sio.on("unlock_door")
def toggle():
    global door_unlocked
    if not door_unlocked:
        door_unlocked = True
        print("Door unlock event received")
        # TODO: implement edge functionality of this code
        sio.emit("unlock_door", True)
        
        # TODO: For now it's 3 seconds, change to 10 seconds later
        eventlet.sleep(3)

        sio.emit("unlock_door", False)
        door_unlocked = False

if __name__ == '__main__':
    print("Starting server...")
    sio.run(app, host='0.0.0.0', port=5500, debug=True)