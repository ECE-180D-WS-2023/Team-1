button_high = False

SUBSCRIPTION = "ECE180/Team1/button/p1"

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