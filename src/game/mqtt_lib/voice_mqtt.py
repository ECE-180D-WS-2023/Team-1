
SUBSCRIPTION = "ECE180/Team1/speech/p1"

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

# The default message callback.
# (you can create separate callbacks per subscribed topic)