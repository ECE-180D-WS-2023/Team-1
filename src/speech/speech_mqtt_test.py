import paho.mqtt.client as mqtt
"""Sample for localization MQTT"""

# 0. define callbacks - functions that run when events happen.
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
  print("Connection returned result: " + str(rc))
  # Subscribing in on_connect() means that if we lose the connection and
  # reconnect then subscriptions will be renewed.
  client.subscribe("ECE180/Team1/button/p2", qos=1)

# The callback of the client when it disconnects.
def on_disconnect(client, userdata, rc):
  if rc != 0:
    print('Unexpected Disconnect')
  else:
    print('Expected Disconnect')

# The default message callback.
# (you can create separate callbacks per subscribed topic)
def on_message(client, userdata, message):
  print('Received message: "' + str(message.payload) + '" on topic "' +
        message.topic + '" with QoS ' + str(message.qos))

# 1. create a client instance.
client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.connect_async('mqtt.eclipseprojects.io')
client.loop_start()

while True:  # perhaps add a stopping condition using some break or something.
  pass  # do your non-blocked other stuff here, like receive IMU data or something.

client.loop_stop()
client.disconnect()