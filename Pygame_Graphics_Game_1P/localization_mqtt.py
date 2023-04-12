player_location = 4
player_coords = 0

SUBSCRIPTION = "ktanna/local"

# on message, just update the player_location that the game is using for localization
def localization_mqtt_on_message(client, userdata, message):
    # print('Received message: "' + str(message.payload) + '" on topic "' +
    #      message.topic + '" with QoS ' + str(message.qos))
    global player_location
    global player_coords
    player_location = int(str(message.payload)[2])
    player_coords = int(str(message.payload)[4:-1])

def localization_mqtt_on_connect(client, userdata, flags, rc):
    print("Connection returned result: " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(SUBSCRIPTION, qos=1)

# The callback of the client when it disconnects.
def localization_mqtt_on_disconnect(client, userdata, rc):
    if rc != 0:
        print('Unexpected Disconnect')
    else:
        print('Expected Disconnect')

# The default message callback.
# (you can create separate callbacks per subscribed topic)