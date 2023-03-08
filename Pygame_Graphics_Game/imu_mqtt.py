# on_message modifies this and stores the motion in this variable
IMU_ACTION = ""
imu_action_received_flag = False

# ACTION CONSTS -- these are unused since just using KEYS in settings
ACTION_UP = 'u'
ACTION_LEFT = 'l'
ACTION_ROTATE = 'r'
ACTION_FORWARD = 'f'


# SHOULD BE ABLE TO MOVE THIS ONE OUT WITH THE SAME WAY points work
# SHOULD BE ABLE TO IMPORT imu_mqtt AND THEN ACCESS WITH imu_mqtt.imu_action_received_flag or whatever
# OR even try imu_mqtt.on_message() for the on message function
# figure out how to move this out this one is bad here
def imu_mqtt_on_message(client, userdata, message):
    # print('Received message: "' + str(message.payload) + '" on topic "' +
    #     message.topic + '" with QoS ' + str(message.qos))
    global IMU_ACTION
    global imu_action_received_flag
    if str(message.payload)[0:3] == "b'1":
        player = 1
        IMU_ACTION = str(message.payload)[3:4]
        imu_action_received_flag = True
        #print(IMU_ACTION)

def imu_mqtt_on_connect(client, userdata, flags, rc):
    print("Connection returned result: " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("ktanna/test", qos=1)

# The callback of the client when it disconnects.
def imu_mqtt_on_disconnect(client, userdata, rc):
    if rc != 0:
        print('Unexpected Disconnect')
    else:
        print('Expected Disconnect')

# The default message callback.
# (you can create separate callbacks per subscribed topic)