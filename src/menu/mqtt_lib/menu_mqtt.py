import re
# start, settings, tutorial, quit, single team, multi team, 1 player, 2 player
START_CLICK = False # key = ga
SETTINGS_CLICK = False # key = sc
TUTORIAL_CLICK = False # key = tc
QUIT_CLICK = False # key = qc
SINGLE_TEAM_CLICK = False # key = st
MULTI_TEAM_CLICK = False # key = mt
ONE_PLAYER_CLICK = False # key = 1p
TWO_PLAYER_CLICK = False # key = 2p
RETURN_CLICK = False # key = rq


SUBSCRIPTION = "ktanna/menu"

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
    if re.search("start", str(message.payload)):
        START_CLICK = True
    elif re.search("settings", str(message.payload)):
        SETTINGS_CLICK = True
    elif re.search("tutorial", str(message.payload)):
        TUTORIAL_CLICK = True
    elif re.search("quit", str(message.payload)):
        QUIT_CLICK = True
    elif re.search("single", str(message.payload)):
        SINGLE_TEAM_CLICK = True
    elif re.search("multi", str(message.payload)):
        MULTI_TEAM_CLICK = True
    elif re.search("1p", str(message.payload)):
        ONE_PLAYER_CLICK = True
    elif re.search("1p", str(message.payload)):
        TWO_PLAYER_CLICK = True
    elif re.search("rq", str(message.payload)):
        RETURN_CLICK = True
    
        

def menu_mqtt_on_connect(client, userdata, flags, rc):
    print("Connection returned result: " + str(rc))
    client.subscribe(SUBSCRIPTION, qos=1)

# The callback of the client when it disconnects.
def menu_mqtt_on_disconnect(client, userdata, rc):
    if rc != 0:
        print('Unexpected Disconnect')
    else:
        print('Expected Disconnect')


# The default message callback.
# (you can create separate callbacks per subscribed topic)