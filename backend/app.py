from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import paho.mqtt.client as mqtt
import json

app = Flask(__name__, template_folder="templates")
CORS(app)

latest_data = {
    "temp": 0,
    "gas": 0
}

BROKER = "broker.hivemq.com"
DATA_TOPIC = "shaik/air/data"
CONTROL_TOPIC = "shaik/air/control"


# MQTT callback
def on_message(client, userdata, msg):
    global latest_data

    payload = msg.payload.decode()
    print("Received:", payload)

    try:
        latest_data = json.loads(payload)
    except Exception as e:
        print("JSON Error:", e)


# MQTT setup
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message

mqtt_client.connect(BROKER, 1883, 60)
mqtt_client.subscribe(DATA_TOPIC)
mqtt_client.loop_start()


# Dashboard route
@app.route('/')
def dashboard():
    return render_template("index.html")


# API route for live data
@app.route('/airdata')
def get_data():
    return jsonify(latest_data)


# API route for LED control
@app.route('/control', methods=['POST'])
def control():
    data = request.json
    command = data.get("command")

    mqtt_client.publish(CONTROL_TOPIC, command)

    return jsonify({
        "status": "success",
        "command": command
    })


# Optional route to see raw JSON directly
@app.route('/status')
def status():
    return jsonify({
        "message": "Flask + MQTT Running",
        "latest_sensor_data": latest_data
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)