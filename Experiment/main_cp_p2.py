from Grid_cp import Grid
from Game_cp import Game
import pygame
import paho.mqtt.client as mqtt
import re
import time

DELAY_PER_FRAME = 700 # ms
DELAY_AFTER_CLICK = 800 # ms

# quitting flag
quit = False


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
        quit = False
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
    client.publish("180team1player2/sub", "P2 Score: " + str(score), qos=1)

#TODO player two flow:
# player two logs on, send P2 on flag
# wait for player one logged on flag
# once player one logged on, start game

# after game ends, publish player two score
# and publish P2 game done
# wait for P1 score 

####### 

# 0. define callbacks - functions that run when events happen.
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
  print("Connection returned result: " + str(rc))
  # Subscribing in on_connect() means that if we lose the connection and
  # reconnect then subscriptions will be renewed.
  client.subscribe("180team1player1/sub", qos=1)
  print("I've subscribed to player two's server!!")

# The callback of the client when it disconnects.
def on_disconnect(client, userdata, rc):
  if rc != 0:
    print('Unexpected Disconnect')
  else:
    print('Expected Disconnect')

#flags
p1_online = False
gameplay = False
p1_score = 0
p1_complete = False
# The default message callback.
# (you can create separate callbacks per subscribed topic)
def on_message(client, userdata, message):
    global p1_online
    global gameplay
    global p1_complete
    global p1_score
    #print('Received message: "' + str(message.payload) + '" on topic "' +
        #message.topic + '" with QoS ' + str(message.qos))
    # should parse message for flag
    # if message = P1 online (use grep)
    if re.search("P1 Online", str(message.payload)):
        # set P1 online flag to true
        print("P1 is online!")
        p1_online = True
    # else if message = P2 done
    elif re.search("P1 Done", str(message.payload)):
        # set gameplay flag to true
        print("P1 is done playing, P2's turn!")
        gameplay = True
    elif re.search("P1 Score", str(message.payload)):
        p1_score = int(re.search(" [0-9]+", str(message.payload))[0])
        print("P1 Score: " + str(p1_score))
    elif re.search("P1 Finished", str(message.payload)):
        p1_complete = True

# 1. create a client instance.
client = mqtt.Client()
# add additional client options (security, certifications, etc.)
# many default options should be good to start off.
# add callbacks to client.
print("Connecting to client...")
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


while True: 
    # P1 logs on
    client.publish("180team1player2/sub", "P2 Online", qos=1)
    #print("P2 online, waiting for p1")
    if p1_online:
        #print("omg p1 is online! gameplay time!!")
        break
    time.sleep(3)

rounds = 0
p2_complete = False

while True: 
    if gameplay and rounds < 2:
        start_game() #start game publishes the score upon game completion
        print("P2 playing, Yay")
        time.sleep(3)
        rounds += 1
        # set gameplay to false
        gameplay = False
        # publish p1 game flag as false
        client.publish("180team1player2/sub", "P2 Done", qos=1)
    elif rounds == 2:
        p2_complete = True
        client.publish("180team1player2/sub", "P2 Finished", qos=1)
        #print("Game over, who won?")
        break
    elif not gameplay and rounds < 1:
        print("P1 is playing, I will wait my turn")
        time.sleep(4)
    if p1_complete and p2_complete:
        print("Game over, who won?")
        break


print("P1 score: " + str(p1_score) + " P2 score: " + str(score))
if p1_score > score:
    print("P1 won! I lost :(")
elif p1_score < score:
    print("I won!!! Yay! :D")
else:
    print("Uh oh, we tied :0")

# use subscribe() to subscribe to a topic and receive messages.
# use publish() to publish messages to the broker.
# use disconnect() to disconnect from the broker.
client.loop_stop()
client.disconnect()

#####################