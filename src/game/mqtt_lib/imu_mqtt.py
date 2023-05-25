import paho.mqtt.client as mqtt
from enum import StrEnum, Enum
from dataclasses import dataclass

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

SUBSCRIPTION = "ktanna/motion"

# on mqtt message, update the flag and also store the action
# the game loop will make the flag false for next action
def imu_mqtt_on_message(client, userdata, message):
    # print('Received message: "' + str(message.payload) + '" on topic "' +
    #     message.topic + '" with QoS ' + str(message.qos))
    global IMU_ACTION_1
    global imu_action_1_received_flag
    global IMU_ACTION_2
    global imu_action_2_received_flag

    print(message.payload)

    if str(message.payload)[0:4] == "b'p1":
        IMU_ACTION_1 = str(message.payload)[5:-1]
        imu_action_1_received_flag = True
    elif str(message.payload)[0:4] == "b'p2":
        IMU_ACTION_2 = str(message.payload)[5:-1]
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

class Action(StrEnum):
    LEFT = "l"
    RIGHT = "r"
    UP = "u"
    ROTATE = "r"
    FORWARD = "f"
    NONE = ""

class Number(Enum):
    PLAYER1 = 1
    PLAYER2 = 2

@dataclass
class Player:
    number: int
    action: Action = Action.NONE
    received_action: bool = False

class IMUListener():

    def __init__(self, topic: str='ktanna/motion', imu_num: int=1):
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

        self.p1 = Player(1)
        self.p2 = Player(2)
        
        self.imu_num = imu_num
        self.action = Action.NONE
        self.received = False

    def debug_set_received(self, player_num: int, val: bool):
        if player_num == self.p1.number:
            self.p1.received_action = val
        elif player_num == self.p2.number:
            self.p2.received_action = val

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

        if "p1" in msg_str or "p2" in msg_str:
            player, action = msg_str.split(',')
            player = (int)(player[1:])

            if player == 1:
                self.p1.action = Action(action)
            elif player == 2:
                self.p2.action = Action(action)
            

if __name__ == "__main__":
    imu = IMUListener('ktanna/motion')

    print(imu.p1.received_action)
    imu.debug_set_received(1, True)
    print(imu.p1.received_action)
    while True:
        pass