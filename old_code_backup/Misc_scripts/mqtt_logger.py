import logging
import time
import paho.mqtt.client as paho
from datetime import datetime


def on_message(client, userdata, message):
    logging.info(str(message.payload.decode("utf-8")))
    print(datetime.now(), "    msg:", str(message.payload.decode("utf-8")))


logging.basicConfig(filename='MKT_mqtt.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

broker = "192.168.20.23"
client = paho.Client("client-001")
client.on_message = on_message

print("connecting to broker ", broker)
client.connect(broker)  # connect
client.loop_start()  # start loop to process received messages

print("subscribing ")
client.subscribe("MKT")  # subscribe
