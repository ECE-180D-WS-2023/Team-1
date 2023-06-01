import re
REMOTE_SUBSCRIPTION = "ECE180/remote"
MQTT_MESSAGE = "" # TODO make global string
MQTT_RECEIVED = False # TODO make global bool
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
    #set MQTT_RECEIVED = True
    #set MQTT_MESSAGE to the received message (with parsed off b')
    global MQTT_RECEIVED
    global MQTT_MESSAGE
    global MQTT_LOBBIES
    global MQTT_TEAM1_READY
    global MQTT_TEAM2_READY
    MQTT_MESSAGE = msg_str
    if re.search(r'^Z', msg_str):
        MQTT_LOBBIES = msg_str
    if re.search(r'T1_READY', msg_str):
        MQTT_TEAM1_READY = True
    if re.search(r'T2_READY', msg_str):
        MQTT_TEAM2_READY = True
    MQTT_RECEIVED = True
    
def server_on_connect(client, userdata, flags, rc):
    print("Remote play connection returned result: " + str(rc))
    client.subscribe(REMOTE_SUBSCRIPTION, qos=1)

# The callback of the client when it disconnects.
def server_on_disconnect(client, userdata, rc):
    if rc != 0:
        print('Unexpected Disconnect: ' + str(rc))
    else:
        print('Expected Disconnect')

def server_on_publish(client, userdata, mid):
    print("MESSAGE PUBLISHED!!! WOOOO")

# The default message callback.
# (you can create separate callbacks per subscribed topic)




# while True:  # perhaps add a stopping condition using some break or something.
#   pass  # do your non-blocked other stuff here, like receive IMU data or something.