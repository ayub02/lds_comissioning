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
    dataBuffer = []
    for x in original2byteDataArray:
        dataBuffer += [(x / 256) % 256, x % 256]
    return dataBuffer


def convertToJsonArray(buff, _topic):
    _myStr = """{"":[""" + ','.join(str(int(x)) for x in completeDataBuffer) + "]}"
    return _myStr[:2] + json_map[_topic] + _myStr[2:]


def convertToJsonArray_delay(buff, _topic):
    _myStr = """{"":[""" + buff + "]}"
    return _myStr[:2] + json_map_delays[_topic] + _myStr[2:]


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
         'BV65': 90166.6, 'BV66': 90447.7, 'BV66A': 126000, 'MOV67': 150005, 'KBS_in': 150502.5, 'KBS_out': 150502.5,
         'MOV68': 151137,
         'BV69': 170633, 'BV70': 175022, 'BV70A': 211423, 'BV71': 239507, 'BV72': 239665, 'BV72A': 273704,
         'MOV73': 283380, 'FSD_in': 283912, 'FSD_out': 283912, 'MOV74': 284521, 'BV74A': 318092, 'BV75': 354986,
         'BV76': 355398, 'MOV77': 363080, 'MCK': 363511}

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

topic_map = {'MKT': 'MKT', 'BV61': 'MW17', 'BV62': 'MW17', 'BV63': 'MW18', 'BV64': 'MW18', 'BV65': 'MW19',
             'BV66': 'MW19', 'BV66A': 'MW19', 'KBS_in': 'KBS', 'KBS_out': 'KBS', 'BV69': 'MW20', 'BV70': 'MW20',
             'BV70A': 'MW21', 'BV71': 'MW22', 'BV72': 'MW22', 'BV72A': 'FSD', 'FSD_in': 'FSD1', 'FSD_out': 'FSD2',
             'BV74A': 'MW24', 'BV75': 'MW25', 'BV76': 'MW25', 'MCK': 'MCK1'}

json_map = {'MKT': 'NPW_array_PT_2003', 'BV61': 'NPW_array_PT_61', 'BV62': 'NPW_array_PT_62',
            'BV63': 'NPW_array_PT_63', 'BV64': 'NPW_array_PT_64', 'BV65': 'NPW_array_PT_65',
            'BV66': 'NPW_array_PT_66', 'BV66A': 'NPW_array_PT_66A', 'KBS_in': 'NPW_array_PT_3025',
            'KBS_out': 'NPW_array_PT_3026', 'BV69': 'NPW_array_PT_69', 'BV70': 'NPW_array_PT_70',
            'BV70A': 'NPW_array_PT_70A', 'BV71': 'NPW_array_PT_71', 'BV72': 'NPW_array_PT_72',
            'BV72A': 'NPW_array_PT_72A', 'FSD_in': 'NPW_array_PT_4025', 'FSD_out': 'NPW_array_PT_4026',
            'BV74A': 'NPW_array_PT_74A', 'BV75': 'NPW_array_PT_75', 'BV76': 'NPW_array_PT_76',
            'MCK': 'NPW_array_PT_5000A'}

json_map_delays = {'MKT': 'PT_2003_delay', 'BV61': 'PT_61_delay', 'BV62': 'PT_62_delay', 'BV63': 'PT_63_delay',
                   'BV64': 'PT_64_delay', 'BV65': 'PT_65_delay', 'BV66': 'PT_66_delay', 'BV66A': 'PT_66A_delay',
                   'KBS_in': 'PT_3025_delay', 'KBS_out': 'PT_3026_delay', 'BV69': 'PT_69_delay', 'BV70': 'PT_70_delay',
                   'BV70A': 'PT_70A_delay', 'BV71': 'PT_71_delay', 'BV72': 'PT_72_delay', 'BV72A': 'PT_72A_delay',
                   'FSD_in': 'PT_4025_delay', 'FSD_out': 'PT_4026_delay', 'BV74A': 'PT_74A_delay', 'BV75': 'PT_75_delay',
                   'BV76': 'PT_76_delay', 'MCK': 'PT_5000A_delay'}

for i, topic in enumerate(topics):
    byteArrayJson = convertToJsonArray_delay('0', topic)
    publislhBuffer(byteArrayJson, topic_map[topic])

    original2byteDataArray = [val * 500 for val in case]
    completeDataBuffer = createTimeBuffer(now_time + timedelta(hours=-5, seconds=rel_times[topic])) + createDataBuffer()
    byteArrayJson = convertToJsonArray(completeDataBuffer, topic)
    publislhBuffer(byteArrayJson, topic_map[topic])
    sleep(delay_between_topics)

    byteArrayJson = convertToJsonArray_delay('1', topic)
    publislhBuffer(byteArrayJson, topic_map[topic])

mqttclient.disconnect()
