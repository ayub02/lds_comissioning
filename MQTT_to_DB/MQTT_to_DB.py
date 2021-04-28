import time
import json
import psycopg2
import sys
import signal
import configparser
from psycopg2 import sql
import paho.mqtt.client as paho
import pandas as pd
from datetime import datetime, timedelta

import logging


def signal_handler(signal, frame):
    print("\nprogram exiting gracefully")
    client.loop_stop()
    print('MQTT stopped')
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("MQTT broker connected OK returned code = %s", rc)
    else:
        logging.error("MQTT broker Bad connection Returned code = %s", rc)


def on_disconnect(client, userdata, rc):
    logging.info("MQTT broker disconnecting reason  "+str(rc))
    client.loop_stop()
    connect_to_client()
    # client.connected_flag = False
    # client.disconnect_flag = True


def on_message(_client, _userdata, _message):
    global cursor, table
    now = datetime.now()
    msg = json.loads(str(_message.payload.decode("utf-8")))
    # print(datetime.now(), '\t\t\t', msg)

    for _val in mqtt_tags:
        if _val in msg:
            logging.info('Data recieved on tag:'+_val)
            if type(msg[_val]) is list:
                str_array = [str(_a) for _a in msg[_val]]
                joined_array = ','.join(str_array)
            elif type(msg[_val]) is float:
                joined_array = msg[_val]

            try:
                _query = sql.SQL(
                    "INSERT INTO {} (itemtimestamp, itemid, itemcurrentvalue) VALUES (TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS'), %s, %s);").format(
                    sql.Identifier(table))
                cursor.execute(_query, (now.strftime("%Y-%m-%d, %H:%M:%S"), _val, joined_array))
            except:
                # logging.error('Database error: %s Code: %s', psycopg2.Error.pgcode, psycopg2.Error.pgerror)
                cursor, table = connect_to_DB()


def connect_to_DB():
    global last_db_connect_time
    if datetime.now() > last_db_connect_time+timedelta(minutes=2):
        last_db_connect_time = datetime.now()
        logging.info('Trying to connect to DB')
        config = configparser.ConfigParser()
        try:
            config.read(config_path)
        except:
            logging.error('Unable to find file: %s', config_path)
        else:
            try:
                _host = config['postgresql']['host']
                _database = config['postgresql']['database']
                _user = config['postgresql']['user']
                _password = config['postgresql']['password']
                _table = config['postgresql']['table']
                _port = config['postgresql']['port']
            except:
                logging.error('Error in format of file: %s', config_path)
            else:
                logging.info('Config file read successfully')
                try:
                    logging.info('Connecting to database: %s and table: %s', _database, _table)
                    _conn = psycopg2.connect(dbname=_database, user=_user, password=_password, host=_host, port=_port)
                except psycopg2.OperationalError as e:
                    print(e.pgcode)
                    logging.error('Database error: %s Code: %s', e.pgcode, e.pgerror)
                    return None, None
                except:
                    e = psycopg2.Error
                    print(e.pgcode)
                    logging.error('Unknown database error')
                    return None, None
                else:
                    logging.info('Connected to database')
                    _conn.autocommit = True
                    _cursor = _conn.cursor()
                    return _cursor, _table
    else:
        return None, None


def connect_to_client():
    while True:
        try:
            client.connect(broker)
        except:
            logging.error('MQTT broker connection failed due to unknown reasons')
        else:
            client.subscribe(mqtt_topics)
            break
        time.sleep(30)
    client.loop_forever()


logging.basicConfig(filename='MQTT_to_DB.log', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.info('********************************************************************************************************')
logging.info('********************************************************************************************************')
logging.info('Program started')
logging.info('********************************************************************************************************')
logging.info('********************************************************************************************************')
config_path = '../config/database.ini'
last_db_connect_time = datetime.now()+timedelta(minutes=-2)

try:
    cursor, table = connect_to_DB()
except:
    pass


tag_data = pd.read_excel('../data/MQTT_tags.xlsx', sheet_name=0)
mqtt_tags = [val for val in tag_data['Periodic'].to_list() + tag_data['NPW'].to_list() if str(val) != 'nan']
print(mqtt_tags)

broker = "192.168.23.12"
mqtt_topics = [('MKT', 1), ('KBS', 1), ('FSD1', 1), ('FSD2', 1), ('MCK1', 1), ('MCK2', 1), ('MW17', 1),
               ('MW18', 1), ('MW19', 1), ('MW20', 1), ('MW21', 1), ('MW22', 1), ('MW23', 1), ('MW24', 1), ('MW25', 1)]

client = paho.Client("client_2")
client.on_message = on_message
client.on_connect = on_connect
client.on_disconnect = on_disconnect
connect_to_client()
# print('Running infinite loop')
# while True:
#     pass
