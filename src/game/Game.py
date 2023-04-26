import pygame
import paho.mqtt.client as mqtt
import logging

from game import mqtt_lib


from .Note import Note, get_lowest_note, SUCCESS, TOO_EARLY, WRONG_KEY, WRONG_LANE
from .Settings import NOTE_SPAWN_SPEED_MS, SCREEN_WIDTH, SCREEN_HEIGHT, HIT_ZONE_LOWER, note_update_time, time_between_motion
from .Settings import LETTER_FONT_SIZE, RESULT_FONT_SIZE, HITZONE_FONT_SIZE, PAUSED_FONT_SIZE
from .Settings import LINE_COLUMN_1, LINE_COLUMN_2, LINE_COLUMN_3, LINE_COLUMN_4, MQTT_CALIBRATION_TIME, LOCALIZATION_CALIBRATION_TIME
from .Player import Player
from .Text import Text
from . import globals

from pygame.locals import (
    K_q,
    K_p,
    KEYDOWN,
    QUIT,
)

# note that height grows downward, the top left is 0, 0 and bottom right is width, height

class Game():
    def __init__(self):
        self.pause = True
        pass

    def start_2p(self):
        # setup vars
        # Initialize pygame
        logging.info(f"GAME: Starting 2P game with: Width:{SCREEN_WIDTH}, Height:{SCREEN_HEIGHT}")
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        logging.info("MQTT: Setting up IMU MQTT Listener")
        # initialize mqtt for imu
        # this mqtt outputs something like "(player#)(action)" e.g., '1r' for player 1 and rotate
        # check imu_mqtt for which channel its listening to
        imu_mqtt_client = mqtt.Client()
        imu_mqtt_client.on_connect = mqtt_lib.imu_mqtt_on_connect
        imu_mqtt_client.on_disconnect = mqtt_lib.imu_mqtt_on_disconnect
        imu_mqtt_client.on_message = mqtt_lib.imu_mqtt_on_message
        imu_mqtt_client.connect_async('mqtt.eclipseprojects.io')
        imu_mqtt_client.loop_start()
        # for initialize mqtt
        pygame.time.wait(MQTT_CALIBRATION_TIME)

        logging.info("MQTT: Setting up Localization MQTT Listener")
        # initialize and calibrate video feed
        # this should output something like "1" for zone 1
        # local = localize(camera=0)
        # local.detect()
        localization_mqtt_client = mqtt.Client()
        localization_mqtt_client.on_connect = mqtt_lib.localization_mqtt_on_connect
        localization_mqtt_client.on_disconnect = mqtt_lib.localization_mqtt_on_disconnect
        localization_mqtt_client.on_message = mqtt_lib.localization_mqtt_on_message
        localization_mqtt_client.connect_async('mqtt.eclipseprojects.io')
        localization_mqtt_client.loop_start()
        pygame.time.wait(LOCALIZATION_CALIBRATION_TIME)
        
        # instantiate sprite groups
        notes = pygame.sprite.Group()
        players = pygame.sprite.Group()
        players.add(Player(1))
        players.add(Player(2))

        # text for hitzone, for results, and points
        hitzone_text = Text(text= "Hit-Zone", rect= (20, HIT_ZONE_LOWER))
        paused_text = Text(text="Press P To Start", rect=(10, SCREEN_HEIGHT/3))
        result_font = pygame.font.Font('fonts/arial.ttf', RESULT_FONT_SIZE)
        points_font = pygame.font.Font('fonts/arial.ttf', RESULT_FONT_SIZE)
        hitzone_font = pygame.font.Font('fonts/arial.ttf', HITZONE_FONT_SIZE)
        paused_font = pygame.font.Font('fonts/arial.ttf', PAUSED_FONT_SIZE)

        # probably will eventually include other sprites like powerups or chars
        all_sprites = pygame.sprite.Group()


        # note spawning timer
        SPAWNNOTE = pygame.USEREVENT + 1
        pygame.time.set_timer(SPAWNNOTE, int(0))

        # received action from imu event for player 1
        ACTION_1 = pygame.USEREVENT + 2
        # where the action is stored
        imu_action_1 = None
        # received action from imu event for player 1
        ACTION_2 = pygame.USEREVENT + 3
        # where the action is stored
        imu_action_2 = None

        # custom note update per speed along with note fall speed
        last_note_update = pygame.time.get_ticks()

        # variable to store result of key_press attempts
        action_input_result = ""

        # Variable to keep the main loop running
        running = True
        while running:
            for event in pygame.event.get():
                # check if q is pressed then leave
                if event.type == KEYDOWN:
                    if event.key == K_q:
                        running = False
                    elif event.key == K_p:
                        self.pause = not self.pause
                        paused_text.update(text="Paused")
                        if (self.pause == True):
                            pygame.time.set_timer(SPAWNNOTE, 0)
                        elif (self.pause == False):
                            pygame.time.set_timer(SPAWNNOTE, int(NOTE_SPAWN_SPEED_MS))


                    else:
                        # calculate which note is the lowest and then process key press accordingly based
                        # on that note's letter
                        if (notes):
                            lowest_note = get_lowest_note(notes)
                            #action_input_result = lowest_note.process_key(pygame.key.name(event.key))
                            #print(localization_mqtt.player_location)
                            action_input_result = lowest_note.process_action_location(pygame.key.name(event.key), mqtt_lib.localization_mqtt.player1_location, 1)
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
                elif event.type == ACTION_1:
                    if (notes):
                        lowest_note = get_lowest_note(notes)
                        # process key works for now since it is just diff letters
                        action_input_result = lowest_note.process_action_location(imu_action_1, mqtt_lib.localization_mqtt.player1_location, 1)
                        self.__calc_points(action_input_result)
                    else:
                        action_input_result = "No Notes Yet!"
                    globals.action_input_result_text.update(text=action_input_result)
                elif event.type == ACTION_2:
                    if (notes):
                        lowest_note = get_lowest_note(notes)
                        # process key works for now since it is just diff letters
                        action_input_result = lowest_note.process_action_location(imu_action_2, mqtt_lib.localization_mqtt.player2_location, 2)
                        self.__calc_points(action_input_result)
                    else:
                        action_input_result = "No Notes Yet!"
                    globals.action_input_result_text.update(text=action_input_result)

            # when pause game, also don't allow action to be read in and dont
            # let there be updated notes
            if not self.pause:
            # if action registered by imu, do the event notification and put the action into imu_action
            # when on_message is called, set some global variable imu_action_received_flag to True and set the action to imu_action
            # because the imu_mqtt runs in parallel, we want to do this flag true and false 
                if (mqtt_lib.imu_mqtt.imu_action_1_received_flag):
                    pygame.event.post(pygame.event.Event(ACTION_1))
                    imu_action_1 = mqtt_lib.imu_mqtt.IMU_ACTION_1
                    print("action received: ", imu_action_1)
                    mqtt_lib.imu_mqtt.imu_action_1_received_flag = False
                if (mqtt_lib.imu_mqtt.imu_action_2_received_flag):
                    pygame.event.post(pygame.event.Event(ACTION_2))
                    imu_action_2 = mqtt_lib.imu_mqtt.IMU_ACTION_2
                    print("action received: ", imu_action_2)
                    mqtt_lib.imu_mqtt.imu_action_2_received_flag = False
                # update note positions
                if (pygame.time.get_ticks() - last_note_update > note_update_time):
                    notes.update()
                    last_note_update = pygame.time.get_ticks()

            # update player location
            players.update()

            # Fill the screen with black
            screen.fill((255, 255, 255))

            # include text to indicate hit zone
            # include text to indicate point record
            # include vertical lines to divide into 4 columns/lanes
            pygame.draw.line(screen, (0, 0, 0), (LINE_COLUMN_1, 0), (LINE_COLUMN_1, SCREEN_HEIGHT))
            pygame.draw.line(screen, (0, 0, 0), (LINE_COLUMN_2, 0), (LINE_COLUMN_2, SCREEN_HEIGHT))
            pygame.draw.line(screen, (0, 0, 0), (LINE_COLUMN_3, 0), (LINE_COLUMN_3, SCREEN_HEIGHT))
            pygame.draw.line(screen, (0, 0, 0), (LINE_COLUMN_4, 0), (LINE_COLUMN_4, SCREEN_HEIGHT))
            # display hit zone
            # horizontal line to indicate hit zone
            pygame.draw.line(screen, (255, 0, 0), (0, HIT_ZONE_LOWER), (SCREEN_WIDTH, HIT_ZONE_LOWER))

            # draw all sprites
            for note in notes:
                screen.blit(note.surf, note.rect)
            for player in players:
                screen.blit(player.surf, player.rect)

            # text for key press results
            screen.blit(result_font.render(globals.action_input_result_text.text, True, (0,0,0)), globals.action_input_result_text.rect)
            # text for points
            globals.points_text.update(text="Points: " + str(globals.points))
            screen.blit(points_font.render(globals.points_text.text, True, (0,0,0)), globals.points_text.rect)
            # text for hitzone indicator
            screen.blit(hitzone_font.render(hitzone_text.text, True, (255,0,0)), hitzone_text.rect)
            
            # text for pause
            if (self.pause):
                print_paused = paused_font.render(paused_text.text, True, (0,0,0))
                print_paused_rect = print_paused.get_rect()
                print_paused_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
                screen.blit(print_paused, print_paused_rect)

            # Update the display
            pygame.display.flip()

    def start_1p(self):
        # setup vars
        # Initialize pygame
        logging.info(f"GAME: Starting 1P game with: Width:{SCREEN_WIDTH}, Height:{SCREEN_HEIGHT}")
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        logging.info("MQTT: Setting up IMU MQTT Listener")
        # initialize mqtt for imu
        # this mqtt outputs something like "(player#)(action)" e.g., '1r' for player 1 and rotate
        # check imu_mqtt for which channel its listening to
        imu_mqtt_client = mqtt.Client()
        imu_mqtt_client.on_connect = mqtt_lib.imu_mqtt_on_connect
        imu_mqtt_client.on_disconnect = mqtt_lib.imu_mqtt_on_disconnect
        imu_mqtt_client.on_message = mqtt_lib.imu_mqtt_on_message
        imu_mqtt_client.connect_async('mqtt.eclipseprojects.io')
        imu_mqtt_client.loop_start()
        # for initialize mqtt
        pygame.time.wait(MQTT_CALIBRATION_TIME)

        logging.info("MQTT: Setting up Localization MQTT Listener")
        # initialize and calibrate video feed
        # this should output something like "1" for zone 1
        # local = localize(camera=0)
        # local.detect()
        localization_mqtt_client = mqtt.Client()
        localization_mqtt_client.on_connect = mqtt_lib.localization_mqtt_on_connect
        localization_mqtt_client.on_disconnect = mqtt_lib.localization_mqtt_on_disconnect
        localization_mqtt_client.on_message = mqtt_lib.localization_mqtt_on_message
        localization_mqtt_client.connect_async('mqtt.eclipseprojects.io')
        localization_mqtt_client.loop_start()
        pygame.time.wait(LOCALIZATION_CALIBRATION_TIME)
        
        # instantiate sprite groups
        notes = pygame.sprite.Group()
        players = pygame.sprite.Group()
        players.add(Player(1))

        # text for hitzone, for results, and points
        hitzone_text = Text(text= "Hit-Zone", rect= (20, HIT_ZONE_LOWER))
        paused_text = Text(text="Press P To Start", rect=(10, SCREEN_HEIGHT/3))
        result_font = pygame.font.Font('fonts/arial.ttf', RESULT_FONT_SIZE)
        points_font = pygame.font.Font('fonts/arial.ttf', RESULT_FONT_SIZE)
        hitzone_font = pygame.font.Font('fonts/arial.ttf', HITZONE_FONT_SIZE)
        paused_font = pygame.font.Font('fonts/arial.ttf', PAUSED_FONT_SIZE)

        # probably will eventually include other sprites like powerups or chars
        all_sprites = pygame.sprite.Group()


        # note spawning timer
        SPAWNNOTE = pygame.USEREVENT + 1
        pygame.time.set_timer(SPAWNNOTE, int(0))

        # received action from imu event
        ACTION_1 = pygame.USEREVENT + 2
        # where the action is stored
        imu_action_1 = None

        # custom note update per speed along with note fall speed
        last_note_update = pygame.time.get_ticks()

        # variable to store result of key_press attempts
        action_input_result = ""

        # Variable to keep the main loop running
        running = True
        while running:
            for event in pygame.event.get():
                # check if q is pressed then leave
                if event.type == KEYDOWN:
                    if event.key == K_q:
                        running = False
                    elif event.key == K_p:
                        self.pause = not self.pause
                        paused_text.update(text="Paused")
                        if (self.pause == True):
                            pygame.time.set_timer(SPAWNNOTE, 0)
                        elif (self.pause == False):
                            pygame.time.set_timer(SPAWNNOTE, int(NOTE_SPAWN_SPEED_MS))


                    else:
                        # calculate which note is the lowest and then process key press accordingly based
                        # on that note's letter
                        if (notes):
                            lowest_note = get_lowest_note(notes)
                            #action_input_result = lowest_note.process_key(pygame.key.name(event.key))
                            #print(localization_mqtt.player_location)
                            action_input_result = lowest_note.process_action_location(pygame.key.name(event.key), mqtt_lib.localization_mqtt.player1_location, 1)
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
                elif event.type == ACTION_1:
                    if (notes):
                        lowest_note = get_lowest_note(notes)
                        # process key works for now since it is just diff letters
                        action_input_result = lowest_note.process_action_location(imu_action_1, mqtt_lib.localization_mqtt.player1_location, 1)
                        self.__calc_points(action_input_result)
                    else:
                        action_input_result = "No Notes Yet!"
                    globals.action_input_result_text.update(text=action_input_result)
            
            # when pause game, also don't allow action to be read in and dont
            # let there be updated notes
            if not self.pause:
            # if action registered by imu, do the event notification and put the action into imu_action
            # when on_message is called, set some global variable imu_action_received_flag to True and set the action to imu_action
            # because the imu_mqtt runs in parallel, we want to do this flag true and false 
                if (mqtt_lib.imu_mqtt.imu_action_1_received_flag):
                    pygame.event.post(pygame.event.Event(ACTION_1))
                    imu_action_1 = mqtt_lib.imu_mqtt.IMU_ACTION_1
                    print("action received: ", imu_action_1)
                    mqtt_lib.imu_mqtt.imu_action_1_received_flag = False
                # update note positions
                if (pygame.time.get_ticks() - last_note_update > note_update_time):
                    notes.update()
                    last_note_update = pygame.time.get_ticks()

            # update player location
            players.update()

            # Fill the screen with black
            screen.fill((255, 255, 255))

            # include text to indicate hit zone
            # include text to indicate point record
            # include vertical lines to divide into 4 columns/lanes
            pygame.draw.line(screen, (0, 0, 0), (LINE_COLUMN_1, 0), (LINE_COLUMN_1, SCREEN_HEIGHT))
            pygame.draw.line(screen, (0, 0, 0), (LINE_COLUMN_2, 0), (LINE_COLUMN_2, SCREEN_HEIGHT))
            pygame.draw.line(screen, (0, 0, 0), (LINE_COLUMN_3, 0), (LINE_COLUMN_3, SCREEN_HEIGHT))
            pygame.draw.line(screen, (0, 0, 0), (LINE_COLUMN_4, 0), (LINE_COLUMN_4, SCREEN_HEIGHT))
            # display hit zone
            # horizontal line to indicate hit zone
            pygame.draw.line(screen, (255, 0, 0), (0, HIT_ZONE_LOWER), (SCREEN_WIDTH, HIT_ZONE_LOWER))

            # draw all sprites
            for note in notes:
                screen.blit(note.surf, note.rect)
            for player in players:
                screen.blit(player.surf, player.rect)

            # text for key press results
            screen.blit(result_font.render(globals.action_input_result_text.text, True, (0,0,0)), globals.action_input_result_text.rect)
            # text for points
            globals.points_text.update(text="Points: " + str(globals.points))
            screen.blit(points_font.render(globals.points_text.text, True, (0,0,0)), globals.points_text.rect)
            # text for hitzone indicator
            screen.blit(hitzone_font.render(hitzone_text.text, True, (255,0,0)), hitzone_text.rect)
            
            # text for pause
            if (self.pause):
                print_paused = paused_font.render(paused_text.text, True, (0,0,0))
                print_paused_rect = print_paused.get_rect()
                print_paused_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
                screen.blit(print_paused, print_paused_rect)

            # Update the display
            pygame.display.flip()

    def __calc_points(self, action_input_result):
        if action_input_result == SUCCESS:
            globals.points += 1
        elif action_input_result == TOO_EARLY or action_input_result == WRONG_KEY or action_input_result == WRONG_LANE:
            # allow players to try again as long as the thing is not gone yet
            # no point deduction for too early or wrong motion
            globals.points -= 0

    