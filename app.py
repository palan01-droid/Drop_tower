# Drop Tower Project - Anuj Pal
# reads FSR 402 sensor data from ESP32 and streams to browser
import serial
import threading
from flask import Flask, render_template_string
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# ── CHANGE THIS to your port when you plug in the ESP32 ──────────────────────
PORT = "/dev/cu.usbserial-0001"
BAUD = 9600
# ─────────────────────────────────────────────────────────────────────────────

def read_serial():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        print(f"Connected to {PORT}")
        while True:
            line = ser.readline().decode("utf-8").strip()
            if "," in line:
                parts = line.split(",")
                if len(parts) == 3:
                    skin, skull, brain = int(parts[0]), int(parts[1]), int(parts[2])
                    socketio.emit("reading", {"skin": skin, "skull": skull, "brain": brain})
    except Exception as e:
        print(f"Serial error: {e}")
        print("Running in DEMO MODE — random data")
        import random, time
        while True:
            socketio.emit("reading", {
                "skin":  random.randint(100, 400),
                "skull": random.randint(80, 300),
                "brain": random.randint(50, 200)
            })
            time.sleep(0.1)

@app.route("/")
def index():
    with open("index.html") as f:
        return f.read()

if __name__ == "__main__":
    t = threading.Thread(target=read_serial, daemon=True)
    t.start()
    print("Open http://localhost:5000 in your browser")
    socketio.run(app, port=5000)
