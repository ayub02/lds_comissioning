import time
import paho.mqtt.client as mqtt
from datetime import datetime
import json
import threading


def tigger_start():
    publislhBuffer('Trig', True, 'BV61')
    print(datetime.now(), '\t', 'Trigger set to True')
    print(datetime.now(), '\t', 'Starting trigger False timer')
    timer2 = threading.Timer(2, tigger_end)
    timer2.start()


def tigger_end():
    publislhBuffer('Trig', False, 'BV61')
    print(datetime.now(), '\t', 'Trigger set to False')


def publislhBuffer(key, val, _topic=None):
    buff = json.dumps({key: val})
    ret = client.publish(_topic, payload=buff, qos=1)
    ret.wait_for_publish()


# define callback
def on_message(client, userdata, message):
    msg = json.dumps(str(message.payload.decode("utf-8")))
    if 'NPW_array' in str(message.payload.decode("utf-8")):
        print(datetime.now(), '\t', 'Event detected')
        print(datetime.now(), '\t', 'Starting trigger True timer')
        timer1 = threading.Timer(2, tigger_start)
        timer1.start()


broker = "10.1.17.112"
client = mqtt.Client("Kepware")
client.on_message = on_message

print(datetime.now(), '\t', "Connecting to broker ", broker)
client.connect(broker)  # connect
client.loop_start()  # start loop to process received messages
print(datetime.now(), '\t', "Subscribing ")
client.subscribe("BV61")  # subscribe

publislhBuffer('BV61', 0, 'delay')
publislhBuffer('BV62', 0, 'delay')
publislhBuffer('BV63', 0, 'delay')

while True:
    pass