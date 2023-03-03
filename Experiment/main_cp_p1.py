from Grid_cp import Grid
from Game_cp import Game
import pygame
import paho.mqtt.client as mqtt

# also do a score check in Game -- 
# because need to quick print grid 
# and also need to print score 
# if score >> some value then move difficulty up

# so Game needs info about score for difficulty
# and main needs info about clicks for updating grid
# actually main shouldn't need to do quick prints
    # just get game to do quick print by passing grid into game method
    # main doesn't even need score... if i really want main
    # to have score just do a game.get_score

DELAY_PER_FRAME = 700 # ms
DELAY_AFTER_CLICK = 800 # ms

# quitting flag
quit = False

# initialize board
my_grid = Grid()
my_game = Game()

# first cycle just print empty grid
my_grid.print_grid()
# need init to use pygame
pygame.init()
WIDTH=100
HEIGHT=100
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))

# keep track of score
score = 0

# function that evaluates button press and then updates the grid
# prints grid how it is currently but just with quick replace on the pressed row/col
def evaluate_press(correct, row, col, grid):
    global score

    if correct < 0 or correct == False:
        grid.set_point(row, col, '-')
        score -= 1
    elif correct == True:
        grid.set_point(row, col, '*')
        score += 1

    grid.print_grid()
    print("Score: ", score)
    if correct == False:
        print("Wrong Key Pressed!")
    elif correct == -1:
        print("Wrong Key Pressed!")
    elif correct == True:
        print("Nice!")
    elif correct == -2:
        print("Pressed Too Early!")
    
    pygame.time.wait(DELAY_AFTER_CLICK)

def start_game():
    # keep printing grid every DELAY_PER_FRAME s for now
    while (True):
        # update game
        my_game.update()

        # reset grid to all . and then update new button location
        my_grid.reset_grid()
        # update grid based on where buttons currently are
        for button in my_game.get_buttons():
            button_row, button_col = button.get_location()
            button_key = button.get_key()
            my_grid.set_point(button_row, button_col, button_key)

        # print grid
        my_grid.print_grid()
        print("Score: ", score)

        # wait certain amount of time before updating screen
        last_time = pygame.time.get_ticks()
        # keypress registering
        correct = None
        row = None
        col = None
        # until new frame time, keep checking for button press
        while(pygame.time.get_ticks() - last_time < DELAY_PER_FRAME):
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        quit = True
                    else:
                        # run function to get which key is pressed
                        correct, row, col = my_game.key_pressed(pygame.key.name(event.key))
                        # then perform print operation
                        evaluate_press(correct, row, col, my_grid)
                        

        if (quit):
            break
    #TODO publish score here ?

#TODO player one flow:
# player one logs on, send P1 on flag
# wait for player two logged on flag
# once player two logged on, start game

# after game ends, publish player one score
# and publish P1 game done
# wait for P2 score 

####### 

# 0. define callbacks - functions that run when events happen.
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
  print("Connection returned result: " + str(rc))
  # Subscribing in on_connect() means that if we lose the connection and
  # reconnect then subscriptions will be renewed.
  client.subscribe("ktissad/test", qos=1)

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
    #TODO
    # should parse message for flag
    # maybe make separate message callbacks for start up and for gameplay?
    # if message = P2 online (use grep)
        # set P2 online flag to true
    # else if message = P2 done
        # set gameplay flag to true

# 1. create a client instance.
client = mqtt.Client()
# add additional client options (security, certifications, etc.)
# many default options should be good to start off.
# add callbacks to client.
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
# 2. connect to a broker using one of the connect*() functions.
# client.connect_async("test.mosquitto.org")
client.connect_async('mqtt.eclipseprojects.io')
# client.connect("test.mosquitto.org", 1883, 60)
# client.connect("mqtt.eclipse.org")
# 3. call one of the loop*() functions to maintain network traffic flow with the broker.
client.loop_start()
# client.loop_forever()

# P1 logs on
client.publish("ktissad/test", "P1 Online", qos=1)

#TODO if p2 online, start while loop:
gameplay = True
p2_online = True

while True: 
    if gameplay:
        start_game() #start game publishes the score upon game completion
        # set gameplay to false
        gameplay = False
    #TODO after game is over, publish score (might need to make game return score)
    #TODO set p1 game flag to false
    pass  # do your non-blocked other stuff here, like receive IMU data or something.

# use subscribe() to subscribe to a topic and receive messages.
# use publish() to publish messages to the broker.
# use disconnect() to disconnect from the broker.
client.loop_stop()
client.disconnect()

#####################