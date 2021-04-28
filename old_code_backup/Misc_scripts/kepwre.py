import paho.mqtt.client as mqtt
import json
import configparser
from time import sleep


def publislhBuffer(buff, _topic=None):
    print(buff)
    ret = mqttclient.publish(_topic, payload=buff, qos=1)
    ret.wait_for_publish()


# Reading configurations
config = configparser.ConfigParser()
config.read('../config/POC_leak_shutin.ini')


# Kepware
mqttHost = config['Kepware']['mqttHost']
mqttPort = int(config['Kepware']['mqttPort'])
mqttclient = mqtt.Client('c1', False)
mqttclient.connect(host=mqttHost, port=mqttPort)  # connect to broker
mqttclient.loop_start()


while True:
    publislhBuffer('Trig', True, _topic='BV61')
    sleep(2)
    publislhBuffer('Trig', False, _topic='BV61')
    sleep(2)

