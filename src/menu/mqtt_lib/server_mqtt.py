REMOTE_SUBSCRIPTION = "ECE180/remote"

def server_on_message(client, userdata, message):
    # may need global variables
    # parse message and set flags
    msg_str = message.payload.decode()
    print(msg_str)
    #set MQTT_RECEIVED = True
    #set MQTT_MESSAGE to the received message (with parsed off b')

    # if we receive a request for list of lobbies publish the list of lobbies
    # client.publish('server', lobbies)
    # if we receive a new lobby add it to the list of lobbies

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