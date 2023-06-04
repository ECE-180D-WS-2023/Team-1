import paho.mqtt.client as mqtt
import time

button_high = False

SUBSCRIPTION = "ECE180/Team1/button"

"""
deprecated
"""

# on message, just update the player_location that the game is using for localization
def button_mqtt_on_message(client, userdata, message):
    global button_high
    msg_str = message.payload.decode() 

    if msg_str == "H":
        button_high = True
    elif msg_str == "L":
        button_high = False

def button_mqtt_on_connect(client, userdata, flags, rc):
    client.subscribe(SUBSCRIPTION, qos=1)
    print("Connection returned result: " + str(rc))

def button_mqtt_on_disconnect(client, userdata, rc):
    if rc != 0:
        print('Unexpected Disconnect')
    else:
        print('Expected Disconnect')
"""
END DEPRECATED
"""

class ButtonListener():

    def __init__(self, topic: str="ECE180/Team1/button/p1") -> None:
        self.topic = topic

        # initialize MQTT values
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.connect_async('mqtt.eclipseprojects.io')
        self.client.loop_start()
        #self.client.publish(self.topic, 1, qos=1)

        self.button_high = False
        self.end_timer = 0.0
        # print(f"INITIALIZED BUTTON at {self.end_timer}")

    def button_active(self, delay: float=0):
        """
        Does the same thing as getting button_high, but 
        includes a delay between end of button press and 
        continued processing
        """
        cur_time = time.time()

        if self.button_high:
            return True

        # print(cur_time-self.end_timer)
        if self.end_timer != 0.0 and \
            cur_time-self.end_timer <= delay:
            # print("DELAY")
            return True

        return False

    def debug_button_set(self, val: bool):
        self.button_high = val

    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.topic, qos=1)
        #print("Connection returned result: " + str(rc))
    
    def _on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print('Unexpected Disconnect')
        else:
            print('Expected Disconnect')

    # on message, just update the player_location that the game is using for localization
    def _on_message(self, client, userdata, message):
        msg_str = message.payload.decode() 
        print(msg_str)

        if msg_str == "H":
            self.button_high = True
        elif msg_str == "L":
            self.button_high = False
            self.end_timer = time.time()
        elif msg_str == "RESET":
            self.button_high = False
            print("GOT RESET"*900)


if __name__ == "__main__":
    but = ButtonListener("ECE180/Team1/button/p2")

    while True:
        # time.sleep(1)
        # print(but.button_high)
        print(but.button_active(1.0))
        pass

