import time
import paho.mqtt.client as paho
from datetime import datetime
import json
broker = "192.168.20.23"


# define callback
def on_message(client, userdata, message):
    msg = json.dumps(str(message.payload.decode("utf-8")))
    if 'PT_2084' in str(message.payload.decode("utf-8")):
        print(datetime.now(), '    ', msg)


client = paho.Client("client-002"
                     "")
client.on_message = on_message

print("connecting to broker ", broker)
client.connect(broker)  # connect
client.loop_start()  # start loop to process received messages
print("subscribing ")
client.subscribe("MKT")  # subscribe

while True:
    pass