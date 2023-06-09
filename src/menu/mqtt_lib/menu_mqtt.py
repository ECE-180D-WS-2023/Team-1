import re
from dataclasses import dataclass
import paho.mqtt.client as mqtt

# start, settings, tutorial, quit, single team, multi team, 1 player, 2 player
START_CLICK = False # key = ga
SETTINGS_CLICK = False # key = sc
TUTORIAL_CLICK = False # key = tc
QUIT_CLICK = False # key = qc
#SINGLE_TEAM_CLICK = False # key = st
MULTI_TEAM_CLICK = False # key = mt
ONE_PLAYER_CLICK = False # key = 1p
TWO_PLAYER_CLICK = False # key = 2p
TEAM_A_CLICK = False
TEAM_B_CLICK = False
RETURN_CLICK = False # key = rq
PLAY_CLICK = False
CREATE_CLICK = False

MESSAGE_RECEIVED = False
SONG_A = False
SONG_B = False
SONG_C = False
SONG_D = False
SONG_E = False
SONG_F = False

SUBSCRIPTION = "ECE180/Team1/speech"

def menu_mqtt_on_message(client, userdata, message):
    # may need global variables
    # parse message and set flags
    global START_CLICK # ga
    global SETTINGS_CLICK # sc
    global TUTORIAL_CLICK # tc
    global QUIT_CLICK # qc
    global SINGLE_TEAM_CLICK # st
    global MULTI_TEAM_CLICK # mt
    global ONE_PLAYER_CLICK # 1p
    global TWO_PLAYER_CLICK # 2p
    global RETURN_CLICK # rq
    global PLAY_CLICK 
    global CREATE_CLICK
    global MESSAGE_RECEIVED
    global SONG_A
    global SONG_B
    global SONG_C
    global SONG_D
    global SONG_E
    global SONG_F
    msg_str = message.payload.decode()
    MESSAGE_RECEIVED = True
    print(msg_str)
    if re.search("start", msg_str):
        print("Received start!")
        START_CLICK = True
    elif re.search("settings", msg_str):
        print("Received settings!")
        SETTINGS_CLICK = True
    elif re.search("tutorial", msg_str):
        print("Received tutorial!")
        TUTORIAL_CLICK = True
    elif re.search("quit", msg_str):
        print("Received quit!")
        QUIT_CLICK = True
    elif re.search("single", msg_str):
        print("Received single!")
        SINGLE_TEAM_CLICK = True
    elif re.search("multi", msg_str):
        print("Received multi!")
        MULTI_TEAM_CLICK = True
    elif re.search("one", msg_str):
        print("Received one player!")
        ONE_PLAYER_CLICK = True
    elif re.search("two", msg_str):
        print("Received two player!")
        TWO_PLAYER_CLICK = True
    elif re.search("return", msg_str):
        print("Received back!")
        RETURN_CLICK = True
    elif re.search("create", msg_str):
        print("Received create!")
        CREATE_CLICK = True
    elif re.search("play", msg_str):
        print("Received play!")
        PLAY_CLICK = True
    elif re.search("a", msg_str):
        print("Received A!")
        SONG_A = True
    elif re.search("b", msg_str):
        print("Received B!")
        SONG_B = True
    elif re.search("c", msg_str):
        print("Received C!")
        SONG_C = True
    elif re.search("d", msg_str):
        print("Received D!")
        SONG_D = True
    elif re.search("e", msg_str):
        print("Received E!")
        SONG_E = True
    elif re.search("f", msg_str):
        print("Received F!")
        SONG_F = True
    
    
        

def menu_mqtt_on_connect(client, userdata, flags, rc):
    print("Speech connection returned result: " + str(rc))
    client.subscribe(SUBSCRIPTION, qos=1)

# The callback of the client when it disconnects.
def menu_mqtt_on_disconnect(client, userdata, rc):
    if rc != 0:
        print('Unexpected Disconnect')
    else:
        print('Expected Disconnect')

@dataclass
class SpeechFlags:
    START_CLICK: bool = False
    SETTINGS_CLICK: bool = False
    TUTORIAL_CLICK: bool = False
    QUIT_CLICK: bool = False
    SINGLE_TEAM_CLICK: bool = False
    MULTI_TEAM_CLICK: bool = False
    ONE_PLAYER_CLICK: bool = False
    TWO_PLAYER_CLICK: bool = False
    RETURN_CLICK: bool = False
    PLAY_CLICK: bool = False
    CREATE_CLICK: bool = False
    MESSAGE_RECEIVED: bool = False
    SONG_A: bool = False
    SONG_B: bool = False
    SONG_C: bool = False
    SONG_D: bool = False
    SONG_E: bool = False
    SONG_F: bool = False


class MenuSpeechListener:
    def __init__(self, topic: str = "ECE180/Team1/speech"):
        # Initialize topic and SpeechFlags datasctructure
        self.topic = topic
        self.sf = SpeechFlags()

        # initialize MQTT values
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.connect_async("mqtt.eclipseprojects.io")
        self.client.loop_start()
        print("Initializing speech listener")

        # Send the connection success message
        # self.client.publish(self.topic, 1, qos=1)

        # Initialize object vars
        self.keyword = ""
        self.received = False

    def debug_set_received(self, val: bool):
        self.received = val

    def debug_set_msg(self, msg: str):
        self.keyword = msg

    def debug_publish(self, msg):
        self.client.publish(self.topic, msg, qos=1)

    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.topic, qos=1)
        print("Speech Connection returned result: " + str(rc))

    def _on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("Unexpected Disconnect")
        else:
            print("Expected Disconnect")

    # On message, just update the player_location that the game
    #   is using for localization
    def _on_message(self, client, userdata, message):
        msg_str = message.payload.decode()
        print(msg_str)
        self.keyword = msg_str
        self.received = True
        self.sf.MESSAGE_RECEIVED = True
        # TODO Find a nicer way to represent this data to make it more easy to
        #   work with
        if re.search("start", msg_str):
            self.sf.START_CLICK = True
        elif re.search("settings", msg_str):
            self.sf.SETTINGS_CLICK = True
            print("settings click" + str(self.sf.SETTINGS_CLICK))
        elif re.search("tutorial", msg_str):
            self.sf.TUTORIAL_CLICK = True
        elif re.search("quit", msg_str):
            self.sf.QUIT_CLICK = True
        elif re.search("single", msg_str):
            self.sf.SINGLE_TEAM_CLICK = True
        elif re.search("multi", msg_str):
            self.sf.MULTI_TEAM_CLICK = True
        elif re.search("one", msg_str):
            self.sf.ONE_PLAYER_CLICK = True
        elif re.search("two", msg_str):
            self.sf.TWO_PLAYER_CLICK = True
        elif re.search("return", msg_str):
            self.sf.RETURN_CLICK = True
        elif re.search("play", msg_str):
            self.sf.PLAY_CLICK = True
        elif re.search("create", msg_str):
            self.sf.CREATE_CLICK = True
        elif re.search("a", msg_str):
            self.sf.SONG_A = True
        elif re.search("b", msg_str):
            self.sf.SONG_B = True
        elif re.search("c", msg_str):
            self.sf.SONG_C = True
        elif re.search("d", msg_str):
            self.sf.SONG_D = True
        elif re.search("e", msg_str):
            self.sf.SONG_E = True
        elif re.search("f", msg_str):
            self.sf.SONG_F = True


if __name__ == "__main__":
    """
    To use the new MenuSpeechListener, you just have to create a
    SpeechFlags Object in the menu.py and instantiate the
    MenuSpeechListener with your SpeechFlags as an argument

    MenuSpeechListener will automatically update your speechflags
    object on receiving a matching mqtt message. You now only need
    to look at your SpeechFlags object's values to get the data.
    Furthermore, you can change the SpeechFlags data to reset the
    listener to receive that data again.
    """

    my_sf = SpeechFlags()

    msl = MenuSpeechListener(flags=my_sf)
    msl.sf.song_a = True

    print(my_sf)

    my_sf.song_a = False

    print(msl.sf.song_a)

