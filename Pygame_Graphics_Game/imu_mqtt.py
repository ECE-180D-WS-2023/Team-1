# on_message modifies this and stores the motion in this variable
IMU_ACTION_1 = ""
imu_action_1_received_flag = False
IMU_ACTION_2 = ""
imu_action_2_received_flag = False

# ACTION CONSTS -- these are unused since just using KEYS in settings
ACTION_UP = 'u'
ACTION_LEFT = 'l'
ACTION_ROTATE = 'r'
ACTION_FORWARD = 'f'

SUBSCRIPTION = "ktanna/test"

# on mqtt message, update the flag and also store the action
# the game loop will make the flag false for next action
def imu_mqtt_on_message(client, userdata, message):
    # print('Received message: "' + str(message.payload) + '" on topic "' +
    #     message.topic + '" with QoS ' + str(message.qos))
    global IMU_ACTION_1
    global imu_action_1_received_flag
    global IMU_ACTION_2
    global imu_action_2_received_flag

    if str(message.payload)[0:4] == "b'p1":
        IMU_ACTION_1 = str(message.payload)[4:-1]
        imu_action_1_received_flag = True
    elif str(message.payload)[0:4] == "b'p2":
        IMU_ACTION_2 = str(message.payload)[4:-1]
        imu_action_2_received_flag = True

def imu_mqtt_on_connect(client, userdata, flags, rc):
    print("Connection returned result: " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(SUBSCRIPTION, qos=1)

# The callback of the client when it disconnects.
def imu_mqtt_on_disconnect(client, userdata, rc):
    if rc != 0:
        print('Unexpected Disconnect')
    else:
        print('Expected Disconnect')

# The default message callback.
# (you can create separate callbacks per subscribed topic)