import pygame
import logging
import paho.mqtt.client as mqtt

# Internal Package imports
from game import mqtt_lib
import speech

# TODO: Move these files to their own packages
from .Note import Note, get_lowest_note, SUCCESS, TOO_EARLY, WRONG_KEY, WRONG_LANE
from .Settings import NOTE_SPAWN_SPEED_MS, SCREEN_WIDTH, SCREEN_HEIGHT, HIT_ZONE_LOWER, update_time, time_between_motion
from .Settings import LETTER_FONT_SIZE, RESULT_FONT_SIZE, HITZONE_FONT_SIZE
from .Settings import COLUMN_1, COLUMN_2, COLUMN_3, COLUMN_4, MQTT_CALIBRATION_TIME, LOCALIZATION_CALIBRATION_TIME
from .Text import Text
from . import globals

from pygame.locals import (
    K_q,
    K_1,
    KEYDOWN,
    QUIT,
)

# TODO: Move this comment to where it matters
# note that height grows downward, the top left is 0, 0 and bottom right is width, height

class Game():
    def __init__(self):
        pass

    def __calc_points(self, action_input_result):
        if action_input_result == SUCCESS:
            globals.points += 1
        elif action_input_result == TOO_EARLY or action_input_result == WRONG_KEY or action_input_result == WRONG_LANE:
            # allow players to try again as long as the thing is not gone yet
            # no point deduction for too early or wrong motion
            globals.points -= 0

    def start(self):
        # setup vars
        # Initialize pygame
        logging.info(f"GAME: Starting the game with: Width:{SCREEN_WIDTH}, Height:{SCREEN_HEIGHT}")
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # initialize mqtt for imu
        # this mqtt outputs something like "(player#)(action)" e.g., '1r' for player 1 and rotate
        # check imu_mqtt for which channel its listening to
        logging.info("MQTT: Preparing IMU MQTT connection")
        imu_mqtt_client = mqtt.Client()
        imu_mqtt_client.on_connect = mqtt_lib.imu_mqtt_on_connect
        imu_mqtt_client.on_disconnect = mqtt_lib.imu_mqtt_on_disconnect
        imu_mqtt_client.on_message = mqtt_lib.imu_mqtt_on_message
        imu_mqtt_client.connect_async('mqtt.eclipseprojects.io')
        imu_mqtt_client.loop_start()
        # for initialize mqtt
        pygame.time.wait(MQTT_CALIBRATION_TIME)

        # initialize and calibrate video feed
        # this should output something like "1" for zone 1
        # local = localize(camera=0)
        # local.detect()
        logging.info("MQTT: Preparing localization MQTT connection")
        localization_mqtt_client = mqtt.Client()
        localization_mqtt_client.on_connect = mqtt_lib.localization_mqtt_on_connect
        localization_mqtt_client.on_disconnect = mqtt_lib.localization_mqtt_on_disconnect
        localization_mqtt_client.on_message = mqtt_lib.localization_mqtt_on_message
        localization_mqtt_client.connect_async('mqtt.eclipseprojects.io')
        localization_mqtt_client.loop_start()
        pygame.time.wait(LOCALIZATION_CALIBRATION_TIME)

        # motion timer
        last_motion = pygame.time.get_ticks()
        
        # instantiate sprite groups
        notes = pygame.sprite.Group()
        # text for hitzone, for results, and points
        hitzone_text = Text(text= "Hit-Zone", rect= (20, HIT_ZONE_LOWER))
        result_font = pygame.font.Font('fonts/arial.ttf', RESULT_FONT_SIZE)
        points_font = pygame.font.Font('fonts/arial.ttf', RESULT_FONT_SIZE)
        hitzone_font = pygame.font.Font('fonts/arial.ttf', HITZONE_FONT_SIZE)

        # probably will eventually include other sprites like powerups or chars
        all_sprites = pygame.sprite.Group()

        # note spawning timer
        SPAWNNOTE = pygame.USEREVENT + 1
        pygame.time.set_timer(SPAWNNOTE, int(NOTE_SPAWN_SPEED_MS))

        # received action from imu event
        ACTION = pygame.USEREVENT + 2
        # where the action is stored
        imu_action = None

        # TODO Button on esp32 remote was pressed
        SPEECH_BUTTON = pygame.USEREVENT + 3
        speech_flag = True

        # custom note update per speed along with note fall speed
        last_time = pygame.time.get_ticks()

        # variable to store result of key_press attempts
        action_input_result = ""

        # TODO: Make this less horrible looking
        # Variable to keep the main loop running
        running = True
        try:
            myrec = speech.KeywordRecognizer(0, speech.config.SPECIAL_WORDS)
            while running:
                for event in pygame.event.get():
                    # check if q is pressed then leave
                    if event.type == KEYDOWN:
                        if event.key == K_q:
                            running = False
                        elif event.key == K_1:
                            print("First pressed")
                            myrec.clear_q()
                            print(f"QUEUE: {myrec.q.queue}")
                        else:
                            # calculate which note is the lowest and then process key press accordingly based
                            # on that note's letter
                            if (notes):
                                lowest_note = get_lowest_note(notes)
                                #action_input_result = lowest_note.process_key(pygame.key.name(event.key))
                                #print(localization_mqtt.player_location)
                                action_input_result = lowest_note.process_action_location(
                                    pygame.key.name(event.key), 
                                    mqtt_lib.localization_mqtt.player_location
                                    )
                                self.__calc_points(action_input_result)
                            else:
                                action_input_result = "No Notes Yet!"
                            globals.action_input_result_text.update(text=action_input_result)
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
                            #print(imu_action)
                            # when handling custom event, reset imu_action_received_flag to False to make sure it doesn't re-trigger
                            lowest_note = get_lowest_note(notes)
                            # FILL IN NOTE'S process_action ONCE ACTIONS ARE KNOWN
                            # process key works for now since it is just diff letters
                            action_input_result = lowest_note.process_action_location(imu_action, localization_mqtt.player_location)
                            self.__calc_points(action_input_result)
                        else:
                            action_input_result = "No Notes Yet!"
                        globals.action_input_result_text.update(text=action_input_result)
                
                # Check if the keyboard or remote button was pressed
                keys = pygame.key.get_pressed()
                if keys[K_1]:
                    speech_flag = True
                else:
                    speech_flag = False

                # Vosk speech recognizer call
                if speech_flag:
                    # print("GETTING SPEECH DATA")
                    d = myrec.get_data()
                    new, word = myrec.test_data(d, verbose=True)
                    if new:
                        print(f"WORD: {word}")
                        if word == "pause":
                            logging.debug("SPEECH: Pause detected")
                            print("PAUSE DETECTED: PAUSING THE GAME")
                        elif word == "exit":
                            logging.debug("SPEECH: Exit detected")
                            print("EXIT DETECTED: EXITING THE GAME")
                            running = False

                # if action registered by imu, do the event notification and put the action into imu_action
                # when on_message is called, set some global variable imu_action_received_flag to True and set the action to imu_action
                # then when imu_action_received is True, do the custom event post
                # in the loop above, when handling custom event, reset imu_action_received_flag to False to make sure it doesn't re-trigger
                if (mqtt_lib.imu_mqtt.imu_action_received_flag):
                    #print("received action flag")
                    if (pygame.time.get_ticks() - last_motion > time_between_motion):
                        #print("action event triggered")
                        pygame.event.post(pygame.event.Event(ACTION))
                        imu_action = mqtt_lib.imu_mqtt.IMU_ACTION
                        last_motion = pygame.time.get_ticks()
                        print("action received: ", imu_action)
                        mqtt_lib.imu_mqtt.imu_action_received_flag = False
                    else:
                        mqtt_lib.imu_mqtt.imu_action_received_flag = False

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
                pygame.draw.line(screen, (255, 0, 0), (0, HIT_ZONE_LOWER), (SCREEN_WIDTH, HIT_ZONE_LOWER))

                # draw all sprites
                for note in notes:
                    screen.blit(note.surf, note.rect)
                
                # text for key press results
                screen.blit(result_font.render(globals.action_input_result_text.text, True, (0,0,0)), globals.action_input_result_text.rect)
                # text for points
                globals.points_text.update(text="Points: " + str(globals.points))
                screen.blit(points_font.render(globals.points_text.text, True, (0,0,0)), globals.points_text.rect)
                # text for hitzone indicator
                screen.blit(hitzone_font.render(hitzone_text.text, True, (255,0,0)), hitzone_text.rect)

                # Update the display
                pygame.display.flip()
        except(KeyboardInterrupt, EOFError):
            print('Received KeyboardInterrupt')