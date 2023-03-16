import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
  print("Connection returned result: " + str(rc))
  client.subscribe("ktanna/test", qos=1)

def on_disconnect(client, userdata, rc):
  if rc != 0:
    print('Unexpected Disconnect')
  else:
    print('Expected Disconnect')

BUTTON_PUSHED = "b'1BUTTON PRESSED"
def on_message(client, userdata, message):
  print('Received message: "' + str(message.payload) + '" on topic "' +
        message.topic + '" with QoS ' + str(message.qos))
  if str(message.payload) == BUTTON_PUSHED:
        # CLIENT 

client = mqtt.Client()

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

client.connect_async('mqtt.eclipseprojects.io')

client.loop_start()

while True:  # perhaps add a stopping condition using some break or something.

  pass  # do your non-blocked other stuff here, like receive IMU data or something.

# use subscribe() to subscribe to a topic and receive messages.
# use publish() to publish messages to the broker.
# use disconnect() to disconnect from the broker.
client.loop_stop()
client.disconnect()