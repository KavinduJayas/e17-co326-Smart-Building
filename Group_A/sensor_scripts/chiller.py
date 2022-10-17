import paho.mqtt.client as mqtt
import json
from time import asctime, time, sleep
from math import exp
import csv


# Chiller On-Model
on_vals = []

with open('chiller-model.csv', 'r') as csvfile:
    csvreader = csv.reader(csvfile)

    for row in csvreader:
        on_vals.append(float(row[1]))

def on_model(temp):
    closest_index = min(range(len(on_vals)), key=lambda i: abs(on_vals[i]-temp))

    return on_vals[closest_index+1]


# Boiler Off Model
off_model = lambda temp, t : 35 + (temp - 35)*exp(-t/2100)


# Initial values
min_temp = 0.0    # Chiller min temp
max_temp = 35.0   # Room temp
temp = max_temp
state = False

# Initialize start time
start_time = time()


# MQTT info
broker_addr = "vpn.ce.pdn.ac.lk"
broker_port = 8883
chiller_topic = "326project/smartbuilding/hvac/control/chiller"
sensor_topic = "326project/smartbuilding/hvac/sensor/chiller"

# Get boiler state via MQTT
def on_message(client, userdata, message):
    global state, start_time

    data = json.loads(message.payload.decode("utf-8"))

    # Update state and start time
    state = True if data['state'] == 1 else False
    print(f"Chiller {'ON' if state is True else 'OFF' }")
    start_time = time()


# Create MQTT client instance and connect to broker
client = mqtt.Client("ChillerDuctTemp")
client.connect(broker_addr, broker_port)
print("Connected to broker")

# Subscribe to relevant topic
client.subscribe(chiller_topic)
print(f"Subscribed to {chiller_topic}")

# Listen for messages
client.on_message = on_message
client.loop_start()


# Publish sensor readings
while True:
    elapsed_time = time() - start_time

    # Update temp value
    match state:
        case True:
            temp = on_model(temp) if temp > min_temp else min_temp

        case False:
            temp = off_model(temp, elapsed_time) if temp < max_temp else max_temp

    # Publish to MQTT topic
    data = json.dumps({"time": asctime(), "temp": round(temp, 2)})
    client.publish(sensor_topic, data)

    print(round(temp,2))
    sleep(1)


# Never runs but added for safety
client.loop_stop()
