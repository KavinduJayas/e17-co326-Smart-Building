import paho.mqtt.client as mqtt
import json
import datetime
import random
import time


mqttBroker = "mqtt.eclipseprojects.io"
client = mqtt.Client("Hot Air Temperature Threashold  value changer")
# client.connect(mqttBroker)

topic = "326project/smartbuilding/hvac/control/temp-thresh-hotairduct"

client.connect("10.40.18.10", port=1883)
x = {
    "time": datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S'),
    "new-humid": random.uniform(10, 20)
}

client.publish(topic, json.dumps(x))
print("published " + str(x) + " to topic " + topic)




