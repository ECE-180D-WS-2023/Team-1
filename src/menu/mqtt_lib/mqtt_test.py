import re
import paho.mqtt.client as mqtt
import sys
import time
sys.path.insert(1, './mqtt_lib/')
import server_mqtt as mqtt_lib


# lobbies = list of tuples (string song, int # players)
lobbies = []

# Setting up the MQTT listener for the server
client = mqtt.Client()
client.on_connect = mqtt_lib.server_on_connect
client.on_disconnect = mqtt_lib.server_on_disconnect
client.on_message = mqtt_lib.server_on_message
client.connect_async('mqtt.eclipseprojects.io')
client.loop_start()
#client.publish(mqtt_lib.REMOTE_SUBSCRIPTION, 1, qos=1)

#lobbies = "ZA1,B2"
lobbies = ""
while (True):
    # try publishing to server
    # client.publish("ECE180/remote", "it's me!!", qos=1)
    # client.publish("ECE180/remote", "T2_READY", qos=1)
    # publish new lobby
    client.publish("ECE180/remote", "A1", qos=1)
    # request lobby list
    client.publish("ECE180/remote", "LLR", qos=1)
    # publish new lobby
    client.publish("ECE180/remote", "B2", qos=1)
    # request lobby list
    client.publish("ECE180/remote", "LLR", qos=1)
    # delay
    time.sleep(3000)