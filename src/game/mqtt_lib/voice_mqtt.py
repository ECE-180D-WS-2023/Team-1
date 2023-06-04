import paho.mqtt.client as mqtt
from dataclasses import dataclass

SUBSCRIPTION = "ECE180/Team1/speech"

voice_received_flag = False
voice_message = ""

# on message, just update the player_location that the game is using for localization
def voice_mqtt_on_message(client, userdata, message):
    # print('Received message: "' + str(message.payload) + '" on topic "' +
    #      message.topic + '" with QoS ' + str(message.qos))
    global voice_received_flag
    global voice_message

    print(message.payload.decode())
    voice_received_flag = True
    voice_message = message.payload.decode()


def voice_mqtt_on_connect(client, userdata, flags, rc):
    print("Connection returned result: " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(SUBSCRIPTION, qos=1)

# The callback of the client when it disconnects.
def voice_mqtt_on_disconnect(client, userdata, rc):
    if rc != 0:
        print('Unexpected Disconnect')
    else:
        print('Expected Disconnect')


class SpeechListener():

    def __init__(self, topic: str='ECE180/Team1/speech/p1'):
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
        print("Connection returned result: " + str(rc))
    
    def _on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print('Unexpected Disconnect')
        else:
            print('Expected Disconnect')

    # on message, just update the player_location that the game is using for localization
    def _on_message(self, client, userdata, message):
        msg_str = message.payload.decode() 
        print(msg_str)

        self.keyword = msg_str
        self.received = True
    

if __name__ == "__main__":
    speech = SpeechListener('ktanna/local')

    print(speech.received)

    # Set the received flag to True
    speech.debug_set_received(True)
    print(speech.received)

    while True:
        if speech.received:
            print(f"Keyword received: {speech.received}")
            speech.debug_set_received(False)

