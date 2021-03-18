import numpy as np
import pandas as pd
import configparser
from time import sleep
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta


class define_time:
    def __init__(self, year, month, day, hour, minute, second, microsecond):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.microsecond = microsecond


def publislhBuffer(buff, _topic=None):
    print(_topic, buff)
    ret = mqttclient.publish(_topic, payload=buff, qos=1)
    ret.wait_for_publish()


# Convert a two digit decimal number into binary coded decimal representation
def bcd(val):
    res = val % 100  # we can BCD encode only two digits in one byte
    res = int(res / 10) * 0x10 + res % 10
    return int(res)


# Creates an an array of 8-byte values to represent timestamp buffer as described above
def createTimeBuffer(t1):
    timeBuffer = [bcd(t1.year - 2000), bcd(t1.month), bcd(t1.day),
                  bcd(t1.hour), bcd(t1.minute), bcd(t1.second),
                  bcd(int(t1.microsecond / 10000)),
                  bcd((int((t1.microsecond - int(t1.microsecond / 10000) * 10000) / 1000) * 10)) + (
                      [2, 3, 4, 5, 6, 7, 1][t1.weekday()])]
    return timeBuffer


# generates a buffer with 200 hypothetical 2-byte pressure values
def createDataBuffer():
    print(original2byteDataArray)
    dataBuffer = []
    for x in original2byteDataArray:
        dataBuffer += [(x / 256) % 256, x % 256]
    return dataBuffer


def convertToJsonArray(buff, _topic):
    _myStr = """{"":[""" + ','.join(str(int(x)) for x in completeDataBuffer) + "]}"
    return _myStr[:2]+json_map[_topic]+_myStr[2:]


# Reading configurations
config = configparser.ConfigParser()
config.read('../config/NPW.ini')

# Kepware
mqttHost = config['Kepware']['mqttHost']
mqttPort = int(config['Kepware']['mqttPort'])

mqttclient = mqtt.Client('c1', False)
mqttclient.connect(host=mqttHost, port=mqttPort)  # connect to broker
mqttclient.loop_start()

dict1 = {'MKT': 0, 'MOV60': 397.5, 'BV61': 18691, 'BV62': 20097, 'BV63': 42458, 'BV64': 42879,
         'BV65': 90166.6, 'BV66': 90447.7, 'MOV67': 150005, 'KBS': 150502.5}
cases = pd.read_excel('../data/NPW_cases.xlsx', sheet_name=0)

# Stations on which to send leak wave data
topics = [val.strip() for val in config['Scenarios']['topics'].split(',')]
class_iter = config['Scenarios']['case_name']
delay_between_topics = int(config['Scenarios']['delay_between_topics'])

case_name = config['Scenarios']['case_name']
case = cases[case_name].tolist()

# Leak location for which pressure wave time stamps will be generated
leak_location = float(config['Scenarios']['leak_location'])  # m

# Speed of sound to be used for generating time stamps
speedOfsound = float(config['Scenarios']['speedOfsound'])  # m/s

# Current time to used as zero reference
now_time = datetime.now()

# Distance of stations relative to leak location
rel_distances = {key: abs(val - leak_location) for key, val in dict1.items()}

# Arrival time of wave at each station relative to time at which the leak is generated (0 seconds)
rel_times = {key: val / speedOfsound for key, val in rel_distances.items()}

topic_map = {'MKT': 'MKT', 'MOV60': 'MKT', 'BV61': 'MW17', 'BV62': 'MW17', 'BV63': 'MW18', 'BV64': 'MW18',
             'BV65': 'MW19', 'BV66': 'MW19', 'MOV67': 'KBS', 'KBS': 'KBS'}

json_map = {'MKT': 'NPW_array_PT_2003', 'MOV60': 'NPW_array_PT_2084', 'BV61': 'NPW_array_PT_61',
            'BV62': 'NPW_array_PT_62', 'BV63': 'NPW_array_PT_63', 'BV64': 'NPW_array_PT_64',
            'BV65': 'NPW_array_PT_65', 'BV66': 'NPW_array_PT_66', 'MOV67': 'NPW_array_PT_3010',
            'KBS': 'NPW_array_PT_3025'}

for i, topic in enumerate(topics):
    sleep(2+np.random.rand()*2)
    original2byteDataArray = [val * 500 for val in case]
    completeDataBuffer = createTimeBuffer(now_time + timedelta(hours=-5, seconds=rel_times[topic])) + createDataBuffer()
    byteArrayJson = convertToJsonArray(completeDataBuffer, topic)
    publislhBuffer(byteArrayJson, topic_map[topic])
    sleep(delay_between_topics)

mqttclient.disconnect()
