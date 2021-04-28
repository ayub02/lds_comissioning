import time
import json
import paho.mqtt.client as paho

broker = "192.168.23.12"


# define callback
def on_message(client, userdata, message):
    msg = json.loads(str(message.payload.decode("utf-8")))
    print(msg)
    # for _key in msg:
    #     if _key == _tag:
    #         now = datetime.now()
    #         print(now, '\t\t\t', _key, '\t\t\t', round(msg[_key], 3))
    #         timestamps.append(now)

mqtt_topics = [('MKT', 1), ('MW17', 1), ('MW18', 1), ('MW19', 1), ('KBS', 1)]

client = paho.Client("client-001")
client.on_message = on_message

print("connecting to broker ", broker)
client.connect(broker)  # connect
print("subscribing ")
client.subscribe(mqtt_topics)  # subscribe

client.loop_forever()  # start loop to process received messages



