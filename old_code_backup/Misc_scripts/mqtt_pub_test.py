import time
import json
from matplotlib import pyplot as plt
import paho.mqtt.client as mqtt
from datetime import datetime
from threading import Timer


class RepeatableTimer(object):
    def __init__(self, interval, function, args=[], kwargs={}):
        self._interval = interval
        self._function = function
        self._args = args
        self._kwargs = kwargs

    def start(self):
        t = Timer(self._interval, self._function, self._args, **self._kwargs)
        t.start()


def hello(_key, _val, _topic):
    print(_key, _val, _topic)


def update_trigger(_key, _val, _topic):
    print(datetime.now(), 'Topic: ', _topic, 'Key: ', _key, 'Val: ', _val)
    ret = mqttclient.publish(_topic, payload=json.dumps({_key: _val}), qos=1)
    ret.wait_for_publish()
    if _val == 0:
        timer_to_1 = RepeatableTimer(timeout_to_1, update_trigger, [_key, 1, _topic])
        timer_to_1.start()


def on_subscribe(client, userdata, mid, granted_qos):
    print(mid, granted_qos)


def on_message(_client, _userdata, message):
    msg = json.dumps(str(message.payload.decode("utf-8")))
    if 'NPW_array_PT_2003' in str(message.payload.decode("utf-8")):
        print(datetime.now(), '\tPT2003')
        timer_to_0 = RepeatableTimer(timeout_to_0, update_trigger, ['PT2003', 0, 'delay'])
        timer_to_0.start()

    if 'NPW_array_PT_61' in str(message.payload.decode("utf-8")):
        print(datetime.now(), '\tPT61')
        timer_to_0 = RepeatableTimer(timeout_to_0, update_trigger, ['PT61', 0, 'delay'])
        timer_to_0.start()

    if 'NPW_array_PT_62' in str(message.payload.decode("utf-8")):
        print(datetime.now(), '\tPT62')
        timer_to_0 = RepeatableTimer(timeout_to_0, update_trigger, ['PT62', 0, 'delay'])
        timer_to_0.start()

    if 'NPW_array_PT_63' in str(message.payload.decode("utf-8")):
        timer_to_0 = RepeatableTimer(timeout_to_0, update_trigger, ['PT63', 0, 'delay'])
        timer_to_0.start()

    if 'NPW_array_PT_64' in str(message.payload.decode("utf-8")):
        timer_to_0 = RepeatableTimer(timeout_to_0, update_trigger, ['PT64', 0, 'delay'])
        timer_to_0.start()

    if 'NPW_array_PT_65' in str(message.payload.decode("utf-8")):
        timer_to_0 = RepeatableTimer(timeout_to_0, update_trigger, ['PT65', 0, 'delay'])
        timer_to_0.start()

    if 'NPW_array_PT_66' in str(message.payload.decode("utf-8")):
        timer_to_0 = RepeatableTimer(timeout_to_0, update_trigger, ['PT66', 0, 'delay'])
        timer_to_0.start()

    if 'NPW_array_PT_3025' in str(message.payload.decode("utf-8")):
        print(datetime.now(), '\tPT3025')
        timer_to_0 = RepeatableTimer(timeout_to_0, update_trigger, ['PT3025', 0, 'delay'])
        timer_to_0.start()


def publislhBuffer(key, _val, _topic=None):
    print(datetime.now(), '\t', _topic, '\t', key, '\t', _val)
    buff = json.dumps({key: _val})
    ret = mqttclient.publish(_topic, payload=buff, qos=1)
    ret.wait_for_publish()


timeout_to_0 = 2
timeout_to_1 = 2

# Kepware
mqttHost = 'localhost'
mqttPort = 1883
mqttclient = mqtt.Client('e1', False)
mqttclient.on_message = on_message
mqttclient.on_subscribe = on_subscribe
mqttclient.connect(host=mqttHost, port=mqttPort)  # connect to broker

mqttclient.subscribe('MKT', 1)
mqttclient.subscribe('MW17', 1)
mqttclient.subscribe('MW18', 1)
mqttclient.subscribe('MW19', 1)
mqttclient.subscribe('KBS', 1)

mqttclient.loop_forever()


