import json
import pandas as pd
import paho.mqtt.client as mqtt
from time import sleep
import multitimer
import time
from datetime import datetime

df = pd.read_csv('periodic_data.csv')
mqttHost = '10.1.17.111'
mqttPort = 1883
mqttclient = mqtt.Client('c1', False)
mqttclient.connect(host=mqttHost, port=mqttPort)  # connect to broker
mqttclient.loop_start()


def hello():
    print(datetime.now())
    for i in range(len(df.index)):
        # print(df.loc[i].topic, '\t', df.loc[i].tag, '\t', df.loc[i].value, '\t', df.loc[i].rate)
        buff = json.dumps({df.loc[i].tag: df.loc[i].value})
        ret = mqttclient.publish(df.loc[i].topic, payload=buff, qos=1)
        ret.wait_for_publish()


t = multitimer.MultiTimer(interval=2, function=hello)
t.start()
