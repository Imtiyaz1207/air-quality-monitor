from flask import Flask, render_template, jsonify
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import os

app = Flask(__name__)

BROKER = "broker.hivemq.com"
TOPIC_DATA = "shaik/air/data"
TOPIC_CONTROL = "shaik/air/control"

latest_data = {"temp": 0, "gas": 0, "time": ""}

# MQTT callback
def on_message(client, userdata, msg):
    global latest_data
    data = json.loads(msg.payload.decode())
    data["time"] = datetime.now().strftime("%H:%M:%S")
    latest_data = data
    print("Received:", data)

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.subscribe(TOPIC_DATA)
client.loop_start()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/data")
def data():
    return jsonify(latest_data)

@app.route("/control/<cmd>")
def control(cmd):
    client.publish(TOPIC_CONTROL, cmd)
    return "OK"

# IMPORTANT for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)