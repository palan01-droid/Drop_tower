# Drop Tower Project - Anuj Pal
# reads FSR 402 sensor data from ESP32 and streams to browser
import os
import serial
import threading
from flask import Flask, render_template_string
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
device_connected = False


SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/cu.usbserial-0001")
BAUD = int(os.getenv("BAUD", "9600"))
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

def read_serial():
    global device_connected
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD, timeout=1)
        print(f"Connected to {SERIAL_PORT}")
        device_connected = True
        socketio.emit("device_status", {"connected": True})
        while True:
            line = ser.readline().decode("utf-8").strip()
            if "," in line:
                parts = line.split(",")
                if len(parts) == 3:
                    skin, skull, brain = int(parts[0]), int(parts[1]), int(parts[2])
                    socketio.emit("reading", {"skin": skin, "skull": skull, "brain": brain})
    except Exception as e:
        print(f"Serial error: {e}")
        device_connected = False
        socketio.emit("device_status", {"connected": False})

@app.route("/")
def index():
    with open("index.html") as f:
        return f.read()

if __name__ == "__main__":
    t = threading.Thread(target=read_serial, daemon=True)
    t.start()
    print(f"Open http://localhost:{SERVER_PORT} in your browser")
    socketio.run(app, host="127.0.0.1", port=SERVER_PORT)
