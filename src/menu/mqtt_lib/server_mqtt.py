import re
import paho.mqtt.client as mqtt
from dataclasses import dataclass
from pprint import pprint

from pygame.mixer_music import rewind


REMOTE_SUBSCRIPTION = "ECE180/remote"
MQTT_MESSAGE = ""  # TODO make global string
MQTT_RECEIVED = False  # TODO make global bool
MQTT_LOBBIES = "Z"
MQTT_TEAM1_READY = False
MQTT_TEAM2_READY = False


def server_on_message(client, userdata, message):
    # may need global variables
    # parse message and set flags
    msg_str = message.payload.decode()
    # if msg_str == "LLR":
    #     print("REQUEST RECEIVED!!!!!!! ")
    print("Server received message: " + msg_str)
    # set MQTT_RECEIVED = True
    # set MQTT_MESSAGE to the received message (with parsed off b')
    global MQTT_RECEIVED
    global MQTT_MESSAGE
    global MQTT_LOBBIES
    global MQTT_TEAM1_READY
    global MQTT_TEAM2_READY
    MQTT_MESSAGE = msg_str
    if re.search(r"^Z", msg_str):
        MQTT_LOBBIES = msg_str
    if re.search(r"T1_READY", msg_str):
        MQTT_TEAM1_READY = True
    if re.search(r"T2_READY", msg_str):
        MQTT_TEAM2_READY = True
    MQTT_RECEIVED = True


def server_on_connect(client, userdata, flags, rc):
    print("Remote play connection returned result: " + str(rc))
    client.subscribe(REMOTE_SUBSCRIPTION, qos=1)


# The callback of the client when it disconnects.
def server_on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected Disconnect: " + str(rc))
    else:
        print("Expected Disconnect")


def server_on_publish(client, userdata, mid):
    print("MESSAGE PUBLISHED!!! WOOOO")


@dataclass
class RemoteFlags:
    received: bool = False
    message: str = ""
    lobbies: str = "Z"  # list[tuple] = []
    t1_ready: bool = False
    t2_ready: bool = False


class RemoteMQTTHandler:
    def __init__(self, remote_data: RemoteFlags, topic: str = "ECE180/remote"):
        # Initialize topic and SpeechFlags datasctructure
        self.topic = topic
        self.rf = remote_data

        # initialize MQTT values
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.connect_async("mqtt.eclipseprojects.io")
        self.client.loop_start()

        # Send the connection success message
        # self.client.publish(self.topic, 1, qos=1)

        # Initialize object vars
        self.msg = ""
        self.received = False

    def debug_set_received(self, val: bool):
        self.received = val

    def debug_set_msg(self, msg: str):
        self.msg = msg

    def debug_publish(self, msg):
        self.client.publish(self.topic, msg, qos=1)

    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.topic, qos=1)
        # print("Connection returned result: " + str(rc))

    def _on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("Unexpected Disconnect")
        else:
            print("Expected Disconnect")

    def _on_message(self, client, userdata, message):
        msg_str = message.payload.decode()
        print(msg_str)

        self.rf.message = msg_str
        self.rf.received = True

        # TODO Find a nicer way to represent this data to make it more easy to
        #   work with
        match msg_str:
            case "T1_READY":
                self.rf.t1_ready = True
            case "T2_READY":
                self.rf.t2_ready = True
            case "LLR":
                print("lobby request...")
                print("current lobby list: " + self.rf.lobbies)
                client.publish("ece180/remote", self.rf.lobbies, qos=1)

        if re.search(r"^Z", msg_str):
            self.rf.lobbies = msg_str

        # If we receive a new lobby add it to the list of lobbies
        new_lobby_pattern = r"^[A-F]"
        if re.search(new_lobby_pattern, msg_str):
            print("Adding lobby...")
            self.rf.lobbies = self.rf.lobbies + "," + msg_str
            print("Current lobby list: " + self.rf.lobbies)


if __name__ == "__main__":
    rem_data = RemoteFlags()
    rem_list = RemoteMQTTHandler(rem_data)

    while True:
        if rem_data.received:
            rem_data.received = False
            rem_data.message = ""
