import re
import paho.mqtt.client as mqtt
import sys
sys.path.insert(1, './mqtt_lib/')
import server_mqtt as mqtt_lib

MQTT_MESSAGE = "" # TODO make global string
MQTT_RECEIVED = False # TODO make global bool

# lobbies = list of tuples (string song, int # players)
lobbies = []

# Setting up the MQTT listener for the server
client = mqtt.Client()
client.on_connect = mqtt_lib.server_on_connect
client.on_disconnect = mqtt_lib.server_on_disconnect
client.on_message = mqtt_lib.server_on_message
client.connect_async('mqtt.eclipseprojects.io')
client.loop_start()
client.publish(mqtt_lib.REMOTE_SUBSCRIPTION, 1, qos=1)

while (True):
    if (MQTT_RECEIVED):
        MQTT_RECEIVED = False
        # parse the message
        MQTT_MESSAGE = "" # clear the message
        # do whatever logic
