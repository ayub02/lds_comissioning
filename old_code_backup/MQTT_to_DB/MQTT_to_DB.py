import time
import json
import psycopg2
import sys
import signal
from psycopg2 import sql
import paho.mqtt.client as paho
from datetime import datetime, timedelta


def signal_handler(signal, frame):
    print("\nProgram exiting gracefully")
    client.loop_stop()
    print('MQTT stopped')
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def on_message(_client, _userdata, _message):
    now = datetime.now()
    msg = json.loads(str(_message.payload.decode("utf-8")))
    # print(datetime.now(), '\t\t\t', msg)

    _tags = ['PT_2084', 'NPW_array_PT_2003', 'NPW_array_PT_2084', 'NPW_array_PT_61', 'NPW_array_PT_62', 'NPW_array_PT_63',
             'NPW_array_PT_64', 'NPW_array_PT_65', 'NPW_array_PT_66', 'NPW_array_PT_3025']

    for _val in _tags:
        if _val in msg:
            print(datetime.now(), '\t\t\t', msg)
            if type(msg[_val]) is list:
                str_array = [str(_a) for _a in msg[_val]]
                joined_array = ','.join(str_array)
            elif type(msg[_val]) is float:
                joined_array = msg[_val]

            _query = sql.SQL(
                "INSERT INTO {} (itemtimestamp, itemid, itemcurrentvalue) VALUES (TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS'), %s, %s);").format(
                sql.Identifier(table))
            cursor.execute(_query, (now.strftime("%Y-%m-%d, %H:%M:%S"), _val, joined_array))


host = 'localhost'
database = 'mqttData'
user = 'postgres'
password = '@intech#123'
table = 'mfmdata30March'
port = 5432

# Connecting to database
while True:
    try:
        print('Connecting to database')
        conn = psycopg2.connect(dbname=database, user=user, password=password, host=host, port=port)
    except psycopg2.OperationalError as e:
        print('Unable to connect!\n{0}'.format(e))
    else:
        print('Connected!')
        break

conn.autocommit = True
cursor = conn.cursor()

broker = "192.168.23.12"
mqtt_topics = [('MKT', 1), ('MW17', 1), ('MW18', 1), ('MW19', 1), ('KBS', 1)]
client = paho.Client("client_2")
client.on_message = on_message
client.connect(broker)

client.subscribe(mqtt_topics)
client.loop_start()
print('Running infinite loop')
while True:
    pass
