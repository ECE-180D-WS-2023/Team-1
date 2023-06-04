import re
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


# The default message callback.
# (you can create separate callbacks per subscribed topic)