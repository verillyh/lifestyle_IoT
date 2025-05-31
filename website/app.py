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
WEB_HOST = "203.101.225.4"

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

# Format logs so that it can be sent over HTTP
def serialize_logs(logs):
    logs_serialized = []

    # Format timestamp
    for row in logs:
        row_copy = dict(row)
        row_copy["timestamp"] = row_copy['timestamp'].isoformat()
        logs_serialized.append(row_copy)
    
    return logs_serialized


@app.route('/logs')
def index():
    global db, cursor

    # Ensure connection hasn't dropped
    db.ping(reconnect=True, attempts=3, delay=2)

    # Check how much results to query based on GET parameter
    try:
        limit_num = int(request.args.get("limit_num", 10))
        if limit_num < 1 or limit_num > 15:
            raise ValueError
    except ValueError:
        return jsonify(error="Invalid limit_num parameter. Please provide only numbers between 1 and 15"), 400
    
    # Retrieve logs from database
    cursor.execute("SELECT * FROM lock_logs ORDER BY timestamp DESC LIMIT %s", (limit_num,)) 

    # Fetch all logs
    logs = cursor.fetchall()
    # Serialize logs
    serialized = serialize_logs(logs)
    print("RETRIEVING LOGS...")
    print(serialized)
    # Return logs
    return jsonify(logs=serialized)

@app.route("/insert_log", methods=["POST"])
def insert_log():
    data = request.get_json()

    # Ensure connection hasn't dropped
    db.ping(reconnect=True, attempts=3, delay=2)
    
    # Get UID and access state
    uid = data.get("uid")
    access = data.get("access")

    # If granted, then emit unlock door event
    if access == "Granted":
        toggle()
    else:
        sio.emit("refresh_data")

    # Try to log into server 
    try:
        cursor.execute("""
            INSERT INTO lock_logs(uid, status) VALUES(%s, %s)
        """, (uid, access))
        db.commit()
        return jsonify({"message": "Successfully inserted log"}), 201 
    except Exception as e:
        print("Error inserting into log: ", e)
        return jsonify({"error": "Can't insert log"}), 500

@sio.on("unlock_door")
def toggle():
    global door_unlocked

    # Only unlock door if it locked
    if not door_unlocked:
        # Set flag
        door_unlocked = True
        print("Door unlock event received")
        
        # Emit unlock event
        sio.emit("unlock_door", True)
        sio.emit("refresh_data")
        # Wait 5s before locking
        eventlet.sleep(5)

        # Emit lock event and set flag
        sio.emit("unlock_door", False)
        sio.emit("refresh_data") 
        door_unlocked = False

if __name__ == '__main__':
    print("Starting server...")
    sio.run(app, host=WEB_HOST, port=5500, debug=True)
