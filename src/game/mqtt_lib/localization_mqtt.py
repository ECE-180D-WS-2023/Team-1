import paho.mqtt.client as mqtt
from dataclasses import dataclass


player1_location = 4
player1_coords = 0

player2_location = 4
player2_coords = 0

SUBSCRIPTION = "ktanna/local"

# on message, just update the player_location that the game is using for localization
def localization_mqtt_on_message(client, userdata, message):
    # print('Received message: "' + str(message.payload) + '" on topic "' +
    #      message.topic + '" with QoS ' + str(message.qos))
    global player1_location
    global player1_coords
    global player2_location
    global player2_coords

    # output of localization looks like:
        # "b'p2,4,109"
        # for player#, zone, absolute position
    # Received message: "b'2,400,1,528'" on topic "ktanna/local" with QoS 1
    # print(message.payload)
    # print(str(message.payload)[3:-1])
    coords_split = str(message.payload)[3:-1].split(",")
    # print(len(coords_split))
    # print(coords_split)
    player1_location = int(coords_split[0])
    player1_coords = int(coords_split[1])
    player2_location = int(coords_split[2])
    player2_coords = int(coords_split[3])

    # print(player1_location, player1_coords, player2_location, player2_coords)

    # if (int(str(message.payload)[3]) == 1):
    #     player1_location = int(str(message.payload)[5])
    #     player1_coords = int(str(message.payload)[7:-1])
    # elif (int(str(message.payload)[3]) == 2):
    #     player2_location = int(str(message.payload)[5])
    #     player2_coords = int(str(message.payload)[7:-1])

def localization_mqtt_on_connect(client, userdata, flags, rc):
    print("Connection returned result: " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(SUBSCRIPTION, qos=1)

# The callback of the client when it disconnects.
def localization_mqtt_on_disconnect(client, userdata, rc):
    if rc != 0:
        print('Unexpected Disconnect')
    else:
        print('Expected Disconnect')


@dataclass
class LocalizationPlayer():
    number: int=0
    location: int=0
    coords: int=0



class LocalizationListener():

    def __init__(self, topic: str='ktanna/local'):
        self.topic = topic

        # initialize MQTT values
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.connect_async('mqtt.eclipseprojects.io')
        self.client.loop_start()
        
        # Send the connection success message
        self.client.publish(self.topic, 1, qos=1)

        self.p1 = LocalizationPlayer(number=1)
        self.p2 = LocalizationPlayer(number=2)

    def debug_set_location(self, player_num: int, val: int):
        if player_num == self.p1.number:
            self.p1.location = val
        elif player_num == self.p2.number:
            self.p2.location = val

    def debug_set_coords(self, player_num: int, val: int):
        if player_num == self.p1.number:
            self.p1.coords = val
        elif player_num == self.p2.number:
            self.p2.coords = val

    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.topic, qos=1)
        print("Connection returned result: " + str(rc))
    
    def _on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print('Unexpected Disconnect')
        else:
            print('Expected Disconnect')

    # on message, just update the player_location that the game is using for localization
    def _on_message(self, client, userdata, message):
        msg_str = message.payload.decode() 
        # print(msg_str)

        msg_split = msg_str.split(',')
        if (len(msg_split) >= 4):
            self.p1.location = int(msg_split[1])
            self.p1.coords = int(msg_split[2])
            self.p2.location = int(msg_split[3])
            self.p2.coords = int(msg_split[4])
        else:
            print("invalid localization message: ", msg_split)
    

if __name__ == "__main__":
    local = LocalizationListener('ktanna/local')

    print(local.p1.location)

    # Set the location of p1 to lane 2
    local.debug_set_location(1, 2)
    print(local.p1.location)

    while True:
        pass

