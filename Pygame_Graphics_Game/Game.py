import pygame
import paho.mqtt.client as mqtt
from mqtt import on_connect, on_disconnect, imu_action_received_flag, IMU_ACTION
from Note import Note, get_lowest_note, SUCCESS, TOO_EARLY, WRONG_KEY
from Settings import NOTE_SPAWN_SPEED_MS, SCREEN_WIDTH, SCREEN_HEIGHT, HIT_ZONE_LOWER, update_time, time_between_motion, LETTER_FONT_SIZE, RESULT_FONT_SIZE
from Settings import COLUMN_1, COLUMN_2, COLUMN_3, COLUMN_4, MQTT_CALIBRATION_TIME
from globals import points
from Text import Text
from pygame.locals import (
    RLEACCEL,
    K_q,
    KEYDOWN,
    QUIT,
)

# figure out how to move this out this one is bad here
def on_message(client, userdata, message):
  #print('Received message: "' + str(message.payload) + '" on topic "' +
        #message.topic + '" with QoS ' + str(message.qos))
    global IMU_ACTION
    global imu_action_received_flag
    if str(message.payload)[0:3] == "b'1":
        player = 1
        IMU_ACTION = str(message.payload)[3:4]
        imu_action_received_flag = True
        #print(IMU_ACTION)

# note that height grows downward, the top left is 0, 0 and bottom right is width, height

class Game():
    # point system when good, increment, when bad, decrement
    def __init__(self):
        pass

    def __calc_points(self, action_input_result):
        global points
        if action_input_result == SUCCESS:
            points += 1
        elif action_input_result == TOO_EARLY or action_input_result == WRONG_KEY:
            # allow players to try again as long as the thing is not gone yet
            # no point deduction for too early or wrong motion
            points -= 0

    def start(self):
        # setup vars
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # initialize mqtt
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_message = on_message
        client.connect_async('mqtt.eclipseprojects.io')
        client.loop_start()
        # for initialize mqtt
        pygame.time.wait(MQTT_CALIBRATION_TIME)


        # vars for gesture recognition
        imu_action = None
        # comes from mqtt setting True and then here, reset to False after processed
        global imu_action_received_flag
        # motion timer
        last_motion = pygame.time.get_ticks()
        
        # instantiate sprite groups
        notes = pygame.sprite.Group()
        # text stuff
        # texts = pygame.sprite.Group().add(Text())
        action_input_result_text = Text(text= "Good Luck!")
        points_text = Text(text= "Points: 0", rect= (SCREEN_WIDTH - (SCREEN_WIDTH/6), 70))
        key_font = pygame.font.Font('fonts/arial.ttf', LETTER_FONT_SIZE)
        result_font = pygame.font.Font('fonts/arial.ttf', RESULT_FONT_SIZE)
        points_font = pygame.font.Font('fonts/arial.ttf', RESULT_FONT_SIZE)

        # probably will eventually include other sprites like powerups or chars
        all_sprites = pygame.sprite.Group()


        # note spawning timer
        SPAWNNOTE = pygame.USEREVENT + 1
        pygame.time.set_timer(SPAWNNOTE, int(NOTE_SPAWN_SPEED_MS))

        # received action from imu event
        ACTION = pygame.USEREVENT + 2
        # where the action is stored
        imu_action = None

        # custom note update per speed along with note fall speed
        last_time = pygame.time.get_ticks()

        # variable to store result of key_press attempts
        action_input_result = ""

        # points printing
        global points

        # Variable to keep the main loop running
        running = True
        while running:
            for event in pygame.event.get():
                # check if q is pressed then leave
                if event.type == KEYDOWN:
                    if event.key == K_q:
                        running = False
                    else:
                        # calculate which note is the lowest and then process key press accordingly based
                        # on that note's letter
                        if (notes):
                            lowest_note = get_lowest_note(notes)
                            action_input_result = lowest_note.process_key(pygame.key.name(event.key))
                            self.__calc_points(action_input_result)
                            points_text.update(text="Points: " + str(points))
                        else:
                            action_input_result = "No Notes Yet!"
                        action_input_result_text.update(text=action_input_result)
                # Check for QUIT event. If QUIT, then set running to false.
                elif event.type == QUIT:
                    running = False
                # spawn note event
                elif event.type == SPAWNNOTE:
                    new_note = Note()
                    notes.add(new_note)
                    all_sprites.add(new_note)
                # if we receive some action from imu
                elif event.type == ACTION:
                    if (notes):
                        #print("should process action")
                        # when handling custom event, reset imu_action_received_flag to False to make sure it doesn't re-trigger
                        lowest_note = get_lowest_note(notes)
                        # FILL IN NOTE'S process_action ONCE ACTIONS ARE KNOWN
                        # process key works for now since it is just diff letters
                        action_input_result = lowest_note.process_key(imu_action)
                        self.__calc_points(action_input_result)
                        points_text.update(text="Points: " + str(points))
                    else:
                        action_input_result = "No Notes Yet!"
                    action_input_result_text.update(text=action_input_result)

            # FILL IN ONCE ACTIONS ARE KNOWN
            # if action registered by imu, do the event notification and put the action into imu_action
            # when on_message is called, set some global variable imu_action_received_flag to True and set the action to imu_action
            # then when imu_action_received is True, do the custom event post
            # in the loop above, when handling custom event, reset imu_action_received_flag to False to make sure it doesn't re-trigger
            if (imu_action_received_flag):
                #print("received action flag")
                if (pygame.time.get_ticks() - last_motion > time_between_motion):
                    #print("action event triggered")
                    pygame.event.post(pygame.event.Event(ACTION))
                    imu_action = IMU_ACTION
                    last_motion = pygame.time.get_ticks()
                    imu_action_received_flag = False
                else:
                    imu_action_received_flag = False

            # update note positions
            if (pygame.time.get_ticks() - last_time > update_time):
                notes.update()
                last_time = pygame.time.get_ticks()

            # Fill the screen with black
            screen.fill((255, 255, 255))

            # include text to indicate hit zone
            # include text to indicate point record
            # include vertical lines to divide into 4 columns/lanes
            pygame.draw.line(screen, (0, 0, 0), (COLUMN_1, 0), (COLUMN_1, SCREEN_HEIGHT))
            pygame.draw.line(screen, (0, 0, 0), (COLUMN_2, 0), (COLUMN_2, SCREEN_HEIGHT))
            pygame.draw.line(screen, (0, 0, 0), (COLUMN_3, 0), (COLUMN_3, SCREEN_HEIGHT))
            pygame.draw.line(screen, (0, 0, 0), (COLUMN_4, 0), (COLUMN_4, SCREEN_HEIGHT))
            # display hit zone
            # horizontal line to indicate hit zone
            pygame.draw.line(screen, (0, 0, 0), (0, HIT_ZONE_LOWER), (SCREEN_WIDTH, HIT_ZONE_LOWER))

            # draw all sprites
            for note in notes:
                screen.blit(note.surf, note.rect)
                # screen.blit(key_font.render(note.letter, True, (255,255,255)), note.rect)
            
            # text for key press results
            screen.blit(result_font.render(action_input_result_text.text, True, (0,0,0)), action_input_result_text.rect)
            # text for points
            screen.blit(points_font.render(points_text.text, True, (0,0,0)), points_text.rect)

            # Update the display
            pygame.display.flip()