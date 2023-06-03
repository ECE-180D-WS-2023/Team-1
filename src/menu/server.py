import re
import paho.mqtt.client as mqtt
import sys
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
lobbies = "Z"
lobbies = mqtt_lib.MQTT_LOBBIES
while (True):
    if (mqtt_lib.MQTT_RECEIVED):
        message = mqtt_lib.MQTT_MESSAGE
        mqtt_lib.MQTT_RECEIVED = False
        mqtt_lib.MQTT_MESSAGE = "" # clear the message
        new_lobby_pattern = r'^[A-F]'
        # parse the message
        # if we receive a request for list of lobbies publish the list of lobbies
        print("Message received = " + message)
        if message == 'LLR':
            print("Lobby request...")
            print("Current lobby list: " + lobbies)
            client.publish("ECE180/remote", lobbies, qos=1)

        # if re.search(r'^Z', message):
        #     mqtt_lib.MQTT_LOBBIES = lobbies
            # print("lobby list published")
            # print("MQTT_LOBBIES = " + mqtt_lib.MQTT_LOBBIES)
            # print("My list: " + lobbies)
        # if we receive a new lobby add it to the list of lobbies
        if re.search(new_lobby_pattern, message):
            print("Adding lobby...")
            lobbies = lobbies + "," + message
            print("Current lobby list: " + lobbies)
        