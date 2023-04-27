import re

# on_message modifies this and stores the motion in this variable
IMU_ACTION = ""
imu_action_received_flag = False

# ACTION CONSTS -- these are unused since just using KEYS in settings
ACTION_UP = 'u'
ACTION_LEFT = 'l'
ACTION_ROTATE = 'r'
ACTION_FORWARD = 'f'

# start, settings, tutorial, quit, single team, multi team, 1 player, 2 player
START_CLICK = False # key = ga
SETTINGS_CLICK = False # key = sc
TUTORIAL_CLICK = False # key = tc
QUIT_CLICK = False # key = qc
SINGLE_TEAM_CLICK = False # key = st
MULTI_TEAM_CLICK = False # key = mt
ONE_PLAYER_CLICK = False # key = 1p
TWO_PLAYER_CLICK = False # key = 2p


SUBSCRIPTION = "ktanna/menu"

def menu_mqtt_on_message(client, userdata, message):
    # may need global variables
    # parse message and set flags
    global START_CLICK
    global SETTINGS_CLICK
    global TUTORIAL_CLICK
    global QUIT_CLICK
    global SINGLE_TEAM_CLICK 
    global MULTI_TEAM_CLICK
    global ONE_PLAYER_CLICK 
    global TWO_PLAYER_CLICK
    if re.search("bing bong", str(message.payload)):
        START_CLICK = True
        

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