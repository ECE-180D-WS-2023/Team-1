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
        remove_lobby_pattern = r'^[R]'
        clear_lobbies = r'^[G]'
        
        num_lobbies = 0
        # parse the message
        # if we receive a request for list of lobbies publish the list of lobbies
        print("Message received = " + message)
        if message == 'LLR':
            #print("Lobby request...")
            #print("Current lobby list: " + lobbies)
            client.publish("ECE180/remote", lobbies, qos=1)
            #mqtt_lib.MQTT_UPDATE_LOBBIES = True
        # if re.search(r'^Z', message):
        #     mqtt_lib.MQTT_LOBBIES = lobbies
            # print("lobby list published")
            # print("MQTT_LOBBIES = " + mqtt_lib.MQTT_LOBBIES)
            # print("My list: " + lobbies)
        # if we receive a new lobby add it to the list of lobbies
        if re.search(new_lobby_pattern, message) and num_lobbies < 6:
            print("Adding lobby...")
            lobbies = lobbies + "," + message
            print("Current lobby list: " + lobbies)
            num_lobbies =+ 1
            mqtt_lib.MQTT_UPDATE_LOBBIES = True
            client.publish("ECE180/remote", 'LLR', qos=1)
        # if num lobbies = 4, need to tell player that they can't make a new lobby
        if num_lobbies == 6:
            print("Max lobbies!")
            # KATIE TODO send signal saying max lobbies reached and trigger bool
            # make sure this is turned off when lobbies < 4
        #KATIE TODO if we receive request to remove lobbies (new flag)
        if re.search(remove_lobby_pattern, message):
            # remove from lobby list and decrement number of lobbies
            r_lobby = "," + message[1:]
            print("removed lobby: " + r_lobby)
            #print("lobbies before: " + lobbies)
            lobbies = lobbies.replace(r_lobby, '')
            mqtt_lib.MQTT_UPDATE_LOBBIES = True
            #print("new lobby list: " + lobbies)
        #KATIE TODO when game starts (new flag)
        if re.search(clear_lobbies, message):
            # clear lobby list
            lobbies = ""
            # set flag to false
            mqtt_lib.MQTT_CLOSE_LOBBIES = False
            # republish lobby list ? idk TODO 