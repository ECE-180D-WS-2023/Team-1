import pygame
import paho.mqtt.client as mqtt
import logging
import random

from game import mqtt_lib

from .Note import Note, FadingNote, get_lowest_note, SUCCESS, TOO_EARLY, WRONG_KEY, WRONG_LANE
from .Settings import SCREEN_WIDTH, SCREEN_HEIGHT, HIT_ZONE_LOWER, note_update_time
from .Settings import NOTE_FALL_SPEED, RESULT_FONT_SIZE, HITZONE_FONT_SIZE, PAUSED_FONT_SIZE
from .Settings import LINE_COLUMN_1, LINE_COLUMN_2, LINE_COLUMN_3, LINE_COLUMN_4, IMU_CALIBRATION_TIME, LOCALIZATION_CALIBRATION_TIME, VOICE_CALIBRATION_TIME, BUTTON_CALIBRATION_TIME
from .Settings import COLOR_1, COLOR_2, PROGRESS_BAR_HEIGHT
from .Progress_Bar import Progress_Bar
from .Player import Player
from .Text import Text
from . import globals

from pygame.locals import (
    K_q,
    K_p,
    K_s,
    K_b, # for mimicking button press
    K_1,
    K_2,
    K_3,
    K_4,
    KEYDOWN,
    QUIT,
)

# note that height grows downward, the top left is 0, 0 and bottom right is width, height

class Game():
    def __init__(self):
        # for pausing game
        self.pause = False
        # for pausing the game while button is pressed
        self.button_pause = False

        # for starting game loop
        self.running = False

        # for starting the actual game inside the game loop
        self.start_game = False

        # bpm of game
        self.bpm = 30
        # song length for calculating progress in progress bar
        self.song_length_seconds = 500

        # notes list
        self.notes = pygame.sprite.Group()
        self.red_notes = pygame.sprite.Group()
        self.blue_notes = pygame.sprite.Group()
        self.fading_notes = pygame.sprite.Group()

        

    def tutorial(self, num_players=2): #tutorial mode of the game (Slow bpm to spawn notes)
        globals.NUM_PLAYERS = num_players
        # set bpm
        self.bpm = 10
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        logging.info(f"Tutorial: Starting {num_players}P tutorial with: Width:{SCREEN_WIDTH}, Height:{SCREEN_HEIGHT}")
      
        logging.info("MQTT: Setting up IMU MQTT Listener")
        imu_mqtt_client = mqtt.Client()
        imu_mqtt_client.on_connect = mqtt_lib.imu_mqtt_on_connect
        imu_mqtt_client.on_disconnect = mqtt_lib.imu_mqtt_on_disconnect
        imu_mqtt_client.on_message = mqtt_lib.imu_mqtt_on_message
        imu_mqtt_client.connect_async('mqtt.eclipseprojects.io')
        imu_mqtt_client.loop_start()
        pygame.time.wait(IMU_CALIBRATION_TIME)

        logging.info("MQTT: Setting up Localization MQTT Listener")
        localization_mqtt_client = mqtt.Client()
        localization_mqtt_client.on_connect = mqtt_lib.localization_mqtt_on_connect
        localization_mqtt_client.on_disconnect = mqtt_lib.localization_mqtt_on_disconnect
        localization_mqtt_client.on_message = mqtt_lib.localization_mqtt_on_message
        localization_mqtt_client.connect_async('mqtt.eclipseprojects.io')
        localization_mqtt_client.loop_start()
        pygame.time.wait(LOCALIZATION_CALIBRATION_TIME)

        # Instantiate sprite groups
        players = pygame.sprite.Group()
        players.add(Player(1))
        if(num_players == 2):
            players.add(Player(2))

        # probably will eventually include other sprites like powerups or chars
        all_sprites = pygame.sprite.Group()

        # text for hitzone, for results, and points
        instructions = {
            'u':" lift remote upward rapidly when note enters hit-zone.",
            'f':" push remote forward rapidly when note enters hit-zone.",
            'l':" swipe remote leftward rapidly when note enters hit-zone.",
            'r':" swipe remote rightward rapidly when note enters hit-zone.",
            1 : "Align box into column of note &",
            2 : "Align box into column of note &",
        }
        hitzone_text = Text(text= "Hit-Zone", rect= (20, HIT_ZONE_LOWER))
        paused_text = Text(text="Paused", rect=(10, SCREEN_HEIGHT/3))
        start_game_text = Text(text="Press S To Start", rect=(10, SCREEN_HEIGHT/3))
        instruction_text = Text(text="", rect=(10, SCREEN_HEIGHT/3))
        result_font = pygame.font.Font('fonts/arial.ttf', RESULT_FONT_SIZE)
        hitzone_font = pygame.font.Font('fonts/arial.ttf', HITZONE_FONT_SIZE)
        paused_font = pygame.font.Font('fonts/arial.ttf', PAUSED_FONT_SIZE)

        SPAWNNOTE = pygame.USEREVENT + 1
        pygame.time.set_timer(SPAWNNOTE, int(0))
        note_spawn_speed_ms = ((1/self.bpm)*60)*1000
        ACTION_1 = pygame.USEREVENT + 2
        imu_action_1 = None
        ACTION_2 = pygame.USEREVENT + 3
        imu_action_2 = None

        last_note_update = pygame.time.get_ticks()
        action_input_result = ""
        if num_players == 1:
            notes_list = [[1,1,'u'], [1,2,'l'], [1,3,'f'], [1,4,'r']] # TO_DO: create lists for player note patterns for tutorial
        else:
            notes_list = [[1,1,'u'], [1,2,'l'], [1,3,'f'], [1,4,'r'], [2,1,'u'], [2,2,'l'], [2,3,'f'], [2,4,'r']]
        if num_players == 1:
            completed_score = 4
        else:
            completed_score = 8
        
        score = 0
        last_score = 0
        points = 0
        self.start_game = False
        self.pause = False
        prev_start_game = False
        player_color=(255,0,0)

        while (score < completed_score):
            for event in pygame.event.get():
                # check if q is pressed then leave
                if event.type == KEYDOWN:
                    if event.key == K_q:
                        score = completed_score
                        break
                    elif event.key == K_s:
                        self.start_game = True
                    elif event.key == K_p:
                        self.pause = not self.pause
                        paused_text.update(text="Paused")
                        if (self.pause == True):
                            pygame.time.set_timer(SPAWNNOTE, 0)
                        elif (self.pause == False):
                            pygame.time.set_timer(SPAWNNOTE, int(note_spawn_speed_ms))
                    elif event.key == K_1 or event.key == K_2 or event.key == K_3 or event.key == K_4:
                        if (event.key == K_1):
                            mqtt_lib.localization_mqtt.player1_location = 1
                            mqtt_lib.localization_mqtt.player1_coords = 560
                        elif (event.key == K_2):
                            mqtt_lib.localization_mqtt.player1_location = 2
                            mqtt_lib.localization_mqtt.player1_coords = 400
                        elif (event.key == K_3):
                            mqtt_lib.localization_mqtt.player1_location = 3
                            mqtt_lib.localization_mqtt.player1_coords = 240
                        elif (event.key == K_4):
                            mqtt_lib.localization_mqtt.player1_location = 4 
                            mqtt_lib.localization_mqtt.player1_coords = 80
                    else:
                        # calculate which note is the lowest and then process key press accordingly based
                        # on that note's letter
                        if (self.notes):
                            lowest_note = get_lowest_note(self.notes)
                            #action_input_result = lowest_note.process_key(pygame.key.name(event.key))
                            #print(localization_mqtt.player_location)
                            action_input_result = lowest_note.process_action_location(pygame.key.name(event.key), mqtt_lib.localization_mqtt.player1_location, 1)
                            self.__calc_points(action_input_result)
                        else:
                            action_input_result = "No Notes Yet!"
                        globals.action_input_result_text.update(text=action_input_result)
                # Check for QUIT event. If QUIT, then set running to false.
                elif event.type == QUIT:
                    break
                # spawn note event
                elif event.type == SPAWNNOTE:
                    color_idx = notes_list[score][0]
                    lane_idx = notes_list[score][1]
                    char_idx = notes_list[score][2]
                    if color_idx == 2:
                        player_color=(0,0,255)
                    instruction_text = Text(text=instructions[color_idx]+instructions[char_idx], rect=(10, SCREEN_HEIGHT/3))
                    new_note = Note(color=color_idx, lane=lane_idx, char=char_idx)
                    self.notes.add(new_note)
                    all_sprites.add(new_note)
                # if we receive some action from imu
                elif event.type == ACTION_1:
                    if (self.notes):
                        lowest_note = get_lowest_note(self.notes)
                        # process key works for now since it is just diff letters
                        action_input_result = lowest_note.process_action_location(imu_action_1, mqtt_lib.localization_mqtt.player1_location, 1)
                        self.__calc_points(action_input_result)
                    else:
                        action_input_result = "No Notes Yet!"
                    globals.action_input_result_text.update(text=action_input_result)
                # this should never be true in 1p bcus action_2 should never be raised
                elif event.type == ACTION_2:
                    if (self.notes):
                        lowest_note = get_lowest_note(self.notes)
                        # process key works for now since it is just diff letters
                        action_input_result = lowest_note.process_action_location(imu_action_2, mqtt_lib.localization_mqtt.player2_location, 2)
                        self.__calc_points(action_input_result)
                    else:
                        action_input_result = "No Notes Yet!"
                    globals.action_input_result_text.update(text=action_input_result)
            
            # same with start_game to start the note timer
            if self.start_game:
                if prev_start_game == False:
                    pygame.time.set_timer(SPAWNNOTE, int(note_spawn_speed_ms))
                prev_start_game = True
            # when pause game, also don't allow action to be read in and dont
            # let there be updated notes
            if self.start_game and not self.pause and not self.button_pause:
            # if action registered by imu, do the event notification and put the action into imu_action
            # when on_message is called, set some global variable imu_action_received_flag to True and set the action to imu_action
            # because the imu_mqtt runs in parallel, we want to do this flag true and false 
                if (mqtt_lib.imu_mqtt.imu_action_1_received_flag):
                    pygame.event.post(pygame.event.Event(ACTION_1))
                    imu_action_1 = mqtt_lib.imu_mqtt.IMU_ACTION_1
                    print("action received: ", imu_action_1)
                    mqtt_lib.imu_mqtt.imu_action_1_received_flag = False
                if (num_players == 2):
                    if (mqtt_lib.imu_mqtt.imu_action_2_received_flag):
                        pygame.event.post(pygame.event.Event(ACTION_2))
                        imu_action_2 = mqtt_lib.imu_mqtt.IMU_ACTION_2
                        print("action received: ", imu_action_2)
                        mqtt_lib.imu_mqtt.imu_action_2_received_flag = False
                # update note positions
                if (pygame.time.get_ticks() - last_note_update > note_update_time):
                    self.notes.update()
                    last_note_update = pygame.time.get_ticks()
            last_score = points
            points = globals.points
            if points > last_score:
                score += 1

            # update player location
            for player in players:
                if (player.player_num == 1):
                    player.update_player_pos(player_num = 1, coords = mqtt_lib.localization_mqtt.player1_coords)
                elif (player.player_num == 2):
                    player.update_player_pos(player_num = 2, coords = mqtt_lib.localization_mqtt.player2_coords)

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
            for note in self.notes:
                screen.blit(note.surf, note.rect)
            for player in players:
                screen.blit(player.surf, player.rect)

            # text for gesture results
            screen.blit(result_font.render(globals.action_input_result_text.text, True, (0,0,0)), globals.action_input_result_text.rect)
            
            # text for hitzone indicator
            screen.blit(hitzone_font.render(hitzone_text.text, True, (255,0,0)), hitzone_text.rect)
            
            # text for pause
            if (self.pause or self.button_pause):
                print_paused, print_paused_rect = self.__clean_print(font=paused_font, Text=paused_text, center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                screen.blit(print_paused, print_paused_rect)
            elif (not self.start_game):
                print_start_game, print_start_game_rect = self.__clean_print(font=paused_font, Text=start_game_text, center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                screen.blit(print_start_game, print_start_game_rect)
                # do not allow the game to be paused while game has not started
                self.pause = False
            else:
                print_inst, print_inst_rect = self.__clean_print(font=result_font, Text=instruction_text, center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2), color=player_color)
                screen.blit(print_inst, print_inst_rect)

            # Update the display
            pygame.display.flip()
        globals.points = 0
        self.start_game = False

    # FOR 2 PLAYER GAME, THE ONLY IF STATEMENTS ARE FOR
    # INITIALIZING THE SECOND PLAYER AND THE IF STATEMENT PROTECTING ACTION_2
    def start(self, num_players=2, song_title="A: "):
        # setup global vars
        # set num players globally so Notes know to only create 1 color
        globals.NUM_PLAYERS = num_players

        # Seed random number generator with seed
        random.seed(song_title)

        # note double spawn probability
        probability_double_note = 0.3

        # clock to limit fps
        clock = pygame.time.Clock()
        fps = 240

        # instantiate progress bar
        progress_bar_width = (3*SCREEN_WIDTH)/4
        progress_bar = Progress_Bar(x= (SCREEN_WIDTH-progress_bar_width)/2, y= PROGRESS_BAR_HEIGHT, width=progress_bar_width, height=15, progress = 0)

        # Initialize pygame
        logging.info(f"GAME: Starting {num_players}P game with: Width:{SCREEN_WIDTH}, Height:{SCREEN_HEIGHT}")
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # initialize sounds and bpm
        pygame.mixer.init()
        self.__load_music(song_title)

        logging.info("MQTT: Setting up IMU MQTT Listener")
        # initialize mqtt for imu
        # this mqtt outputs something like "(player#)(action)" e.g., '1r' for player 1 and right
        # check imu_mqtt for which channel its listening to
        imu_mqtt_client = mqtt.Client()
        imu_mqtt_client.on_connect = mqtt_lib.imu_mqtt_on_connect
        imu_mqtt_client.on_disconnect = mqtt_lib.imu_mqtt_on_disconnect
        imu_mqtt_client.on_message = mqtt_lib.imu_mqtt_on_message
        imu_mqtt_client.connect_async('mqtt.eclipseprojects.io')
        imu_mqtt_client.loop_start()
        # for initialize mqtt
        pygame.time.wait(IMU_CALIBRATION_TIME)

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
        
        logging.info("MQTT: Setting up Voice Recog MQTT Listener")
        voice_mqtt_client = mqtt.Client()
        voice_mqtt_client.on_connect = mqtt_lib.voice_mqtt_on_connect
        voice_mqtt_client.on_disconnect = mqtt_lib.voice_mqtt_on_disconnect
        voice_mqtt_client.on_message = mqtt_lib.voice_mqtt_on_message
        voice_mqtt_client.connect_async('mqtt.eclipseprojects.io')
        voice_mqtt_client.loop_start()
        pygame.time.wait(VOICE_CALIBRATION_TIME)

        logging.info("MQTT: Setting up Button MQTT Listener")
        button_mqtt_client = mqtt.Client()
        button_mqtt_client.on_connect = mqtt_lib.button_mqtt_on_connect
        button_mqtt_client.on_disconnect = mqtt_lib.button_mqtt_on_disconnect
        button_mqtt_client.on_message = mqtt_lib.button_mqtt_on_message
        button_mqtt_client.connect_async('mqtt.eclipseprojects.io')
        button_mqtt_client.loop_start()
        pygame.time.wait(BUTTON_CALIBRATION_TIME)

        # instantiate sprite groups
        players = pygame.sprite.Group()
        players.add(Player(1))
        if(num_players == 2):
            players.add(Player(2))

        # text for hitzone, for results, and points
        hitzone_text = Text(text= "Hit-Zone", rect= (20, HIT_ZONE_LOWER))
        paused_text = Text(text="Paused", rect=(10, SCREEN_HEIGHT/3))
        start_game_text = Text(text="Press S To Start", rect=(10, SCREEN_HEIGHT/3))
        result_font = pygame.font.Font('fonts/arial.ttf', RESULT_FONT_SIZE)
        points_font = pygame.font.Font('fonts/arial.ttf', RESULT_FONT_SIZE)
        hitzone_font = pygame.font.Font('fonts/arial.ttf', HITZONE_FONT_SIZE)
        paused_font = pygame.font.Font('fonts/arial.ttf', PAUSED_FONT_SIZE)

        # probably will eventually include other sprites like powerups or chars
        all_sprites = pygame.sprite.Group()

        # note spawning timer
        SPAWNNOTE = pygame.USEREVENT + 1
        pygame.time.set_timer(SPAWNNOTE, int(0))
        # calculate note spawn speed according to bpm
        note_spawn_speed_ms = ((1/self.bpm)*60)*1000*3
        
        # note spawning offset to have clear time match beat
        note_spawn_delay = int((NOTE_FALL_SPEED*(HIT_ZONE_LOWER + (SCREEN_HEIGHT-HIT_ZONE_LOWER)*(1/3)) / fps))*1000
        # start delay bool
            # once this bool is true, we will check when to actually start the timer
            # when starting timer, reset to false
        start_note_spawn_delay = False
        start_note_spawn_timestamp = 0

        # received action from imu event for player 1
        ACTION_1 = pygame.USEREVENT + 2
        # where the action is stored
        imu_action_1 = None
        
        # this is here defined as an event even if unused when only 1p
        # received action from imu event for player 2
        ACTION_2 = pygame.USEREVENT + 3
        # where the action is stored
        imu_action_2 = None

        # custom note update per speed along with note fall speed
        last_note_update = pygame.time.get_ticks()

        # variable to store result of key_press attempts
        action_input_result = ""

        # stores previous pause state to know whether we resumed or not to continue note generation
        prev_pause = False
        prev_start_game = False

        # Variable to keep the main loop running
        self.running = True
        while self.running:
            for event in pygame.event.get():
                # check if q is pressed then leave
                if event.type == KEYDOWN:
                    if event.key == K_q:
                        self.running = False
                    elif event.key == K_p:
                        self.pause = not self.pause
                    elif event.key == K_s:
                        self.start_game = True
                    elif event.key == K_b:
                        mqtt_lib.button_mqtt.button_high = not mqtt_lib.button_mqtt.button_high
                    elif event.key == K_1 or event.key == K_2 or event.key == K_3 or event.key == K_4:
                        if (event.key == K_1):
                            mqtt_lib.localization_mqtt.player1_location = 1
                            mqtt_lib.localization_mqtt.player1_coords = 560
                        elif (event.key == K_2):
                            mqtt_lib.localization_mqtt.player1_location = 2
                            mqtt_lib.localization_mqtt.player1_coords = 400
                        elif (event.key == K_3):
                            mqtt_lib.localization_mqtt.player1_location = 3
                            mqtt_lib.localization_mqtt.player1_coords = 240
                        elif (event.key == K_4):
                            mqtt_lib.localization_mqtt.player1_location = 4 
                            mqtt_lib.localization_mqtt.player1_coords = 80
                    else:
                        # calculate which note is the lowest and then process key press accordingly based
                        # on that note's letter
                        if (self.red_notes.sprites()):
                            lowest_note = get_lowest_note(self.red_notes)
                            #action_input_result = lowest_note.process_key(pygame.key.name(event.key))
                            #print(localization_mqtt.player_location)
                            action_input_result = lowest_note.process_action_location(pygame.key.name(event.key), mqtt_lib.localization_mqtt.player1_location, 1)
                            self.__calc_points(action_input_result)
                        else:
                            action_input_result = "No Notes Yet!"
                        globals.action_input_result_text.update(text=action_input_result)
                # Check for QUIT event. If QUIT, then set running to false.
                elif event.type == QUIT:
                    self.running = False
                # spawn note event
                elif event.type == SPAWNNOTE:
                    # if 2 players and with 40% maybe probability, spawn both notes, 
                    # maybe this value can increase with game for difficulty
                    double_note_spawn = (num_players == 2) and (random.randint(1, 100)/100.0 < probability_double_note)
                    
                    # if double note spawn, spawn one of each color
                    if (double_note_spawn):
                        new_note_1 = Note(color=1)
                        self.notes.add(new_note_1)
                        all_sprites.add(new_note_1)
                        self.red_notes.add(new_note_1)
                    
                        # make sure the two notes are not in the same lane
                        # while in the same lane, keep making new
                        new_note_2 = Note(color=2)
                        while (new_note_2.lane == new_note_1.lane):
                            new_note_2 = Note(color=2)
                        self.notes.add(new_note_2)
                        all_sprites.add(new_note_2)
                        self.blue_notes.add(new_note_2)
                    # else spawn normally (this spawns red only in 1 player and randomly between the 2 in 2 player)
                    else:
                        new_note = Note()
                        self.notes.add(new_note)
                        all_sprites.add(new_note)
                        if (new_note.color == COLOR_1):
                            self.red_notes.add(new_note)
                        elif (new_note.color == COLOR_2):
                            self.blue_notes.add(new_note)
                    
                # if we receive some action from imu
                elif event.type == ACTION_1:
                    if (self.red_notes.sprites()):
                        lowest_note = get_lowest_note(self.red_notes)
                        # process key works for now since it is just diff letters
                        action_input_result = lowest_note.process_action_location(imu_action_1, mqtt_lib.localization_mqtt.player1_location, 1)
                        self.__calc_points(action_input_result)
                    else:
                        action_input_result = "No Notes Yet!"
                    globals.action_input_result_text.update(text=action_input_result)
                # this should never be true in 1p bcus action_2 should never be raised
                elif event.type == ACTION_2:
                    if (self.blue_notes.sprites()):
                        lowest_note = get_lowest_note(self.blue_notes)
                        # process key works for now since it is just diff letters
                        action_input_result = lowest_note.process_action_location(imu_action_2, mqtt_lib.localization_mqtt.player2_location, 2)
                        self.__calc_points(action_input_result)
                    else:
                        action_input_result = "No Notes Yet!"
                    globals.action_input_result_text.update(text=action_input_result)


            # handle voice recognition stuff
            if mqtt_lib.voice_mqtt.voice_received_flag:
                self.__interpret_voice_recog(mqtt_lib.voice_mqtt.voice_message)
                mqtt_lib.voice_mqtt.voice_received_flag = False
            # handling pause -> unpause transition to resume note spawning timer
                # if we just started to pause, set note spawning timer to 0
                # if we just resumed the game, set note spawning timer back to normal
            if self.pause or self.button_pause:
                if prev_pause == False:
                    pygame.time.set_timer(SPAWNNOTE, 0)
                    pygame.mixer.music.pause()
                prev_pause = True
            else:
                if prev_pause == True:
                    start_note_spawn_delay = True
                    start_note_spawn_timestamp = pygame.time.get_ticks()
                    #pygame.time.set_timer(SPAWNNOTE, int(note_spawn_speed_ms))
                    pygame.mixer.music.unpause()
                prev_pause = False
            # same with start_game to start the note timer and start music
            if self.start_game:
                if prev_start_game == False:
                    start_note_spawn_delay = True
                    start_note_spawn_timestamp = pygame.time.get_ticks()
                    #pygame.time.set_timer(SPAWNNOTE, int(note_spawn_speed_ms))
                    pygame.mixer.music.play()
                prev_start_game = True


            # when pause game, also don't allow action to be read in and dont
            # let there be updated notes
            if self.start_game and not (self.pause or self.button_pause):
            # if action registered by imu, do the event notification and put the action into imu_action
            # when on_message is called, set some global variable imu_action_received_flag to True and set the action to imu_action
            # because the imu_mqtt runs in parallel, we want to do this flag true and false 
                if (mqtt_lib.imu_mqtt.imu_action_1_received_flag):
                    pygame.event.post(pygame.event.Event(ACTION_1))
                    imu_action_1 = mqtt_lib.imu_mqtt.IMU_ACTION_1
                    print("action received: ", imu_action_1)
                    mqtt_lib.imu_mqtt.imu_action_1_received_flag = False
                if (num_players == 2):
                    if (mqtt_lib.imu_mqtt.imu_action_2_received_flag):
                        pygame.event.post(pygame.event.Event(ACTION_2))
                        imu_action_2 = mqtt_lib.imu_mqtt.IMU_ACTION_2
                        print("action received: ", imu_action_2)
                        mqtt_lib.imu_mqtt.imu_action_2_received_flag = False
                # update note positions
                if (pygame.time.get_ticks() - last_note_update > note_update_time):
                    self.notes.update()
                    last_note_update = pygame.time.get_ticks()

            # update player location
            for player in players:
                if (player.player_num == 1):
                    player.update_player_pos(player_num = 1, coords = mqtt_lib.localization_mqtt.player1_coords)
                elif (player.player_num == 2):
                    player.update_player_pos(player_num = 2, coords = mqtt_lib.localization_mqtt.player2_coords)

            # check if there are any notes that need fading
            for note in self.notes:
                if note.fade:
                    fading_note = FadingNote(note)
                    self.fading_notes.add(fading_note)
                    note.fade = False
            # update fading notes animation
            self.fading_notes.update()

            # Fill the screen with black
            screen.fill((255, 255, 255))

            # draw progress bar
            progress_bar.draw(screen, (255, 255, 255), (0, 255, 0))

            # include text to indicate hit zone
            # include text to indicate point record
            # include vertical lines to divide into 4 columns/lanes
            pygame.draw.line(screen, (0, 0, 0), (LINE_COLUMN_1, 0), (LINE_COLUMN_1, SCREEN_HEIGHT))
            pygame.draw.line(screen, (0, 0, 0), (LINE_COLUMN_2, 0), (LINE_COLUMN_2, SCREEN_HEIGHT))
            pygame.draw.line(screen, (0, 0, 0), (LINE_COLUMN_3, 0), (LINE_COLUMN_3, SCREEN_HEIGHT))
            pygame.draw.line(screen, (0, 0, 0), (LINE_COLUMN_4, 0), (LINE_COLUMN_4, SCREEN_HEIGHT))

            # draw all sprites
            for note in self.notes:
                screen.blit(note.surf, note.rect)
            for fading_note in self.fading_notes:
                screen.blit(fading_note.surf, fading_note.rect)
            for player in players:
                screen.blit(player.surf, player.rect)

            # text for gesture results
            screen.blit(result_font.render(globals.action_input_result_text.text, True, (0,0,0)), globals.action_input_result_text.rect)
            
            # update text for points
            globals.points_text.update(text="Points: " + str(globals.points))
            # print points
            # screen.blit(points_font.render(globals.points_text.text, True, (0,0,0)), globals.points_text.rect)
            print_points, print_points_rect = self.__clean_print(font=points_font, Text=globals.points_text, center=globals.points_text.rect, color=(0,0,0))
            screen.blit(print_points, print_points_rect)

            # text for hitzone indicator
            screen.blit(hitzone_font.render(hitzone_text.text, True, (255,0,0)), hitzone_text.rect)
            # display hit zone
            # horizontal line to indicate hit zone
            pygame.draw.line(screen, (255, 0, 0), (0, HIT_ZONE_LOWER), (SCREEN_WIDTH, HIT_ZONE_LOWER))

            # if game hasnt started yet, set progress to 0 and display the startgame text
            if (not self.start_game):
                self.progress = 0
                
                print_start_game, print_start_game_rect = self.__clean_print(font=paused_font, Text=start_game_text, center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                screen.blit(print_start_game, print_start_game_rect)
                # do not allow the game to be paused while game has not started
                self.pause = False
                self.button_pause = False
            
            # text for pause
            if (self.pause or self.button_pause):
                print_paused, print_paused_rect = self.__clean_print(font=paused_font, Text=paused_text, center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                screen.blit(print_paused, print_paused_rect)

            # Update the display
            pygame.display.flip()

            # if need delay before starting note spawn
            if (start_note_spawn_delay):
                # if current time - when we started delay > note_spawn_delay, tjem we start s[awmomg mptes amd set delay false
                if (pygame.time.get_ticks() - start_note_spawn_timestamp >= note_spawn_delay):
                    start_note_spawn_delay = False
                    pygame.time.set_timer(SPAWNNOTE, int(note_spawn_speed_ms))

            # stop game if music done
            if self.start_game:
                if not (self.pause or self.button_pause):
                    if not pygame.mixer.music.get_busy():
                        self.running = False
            # stop music if game done
            if (self.running == False):
                pygame.mixer.music.stop()
                pygame.time.set_timer(SPAWNNOTE, int(0))
                self.__game_over_cleanup()
            
            # set self.button_pause when button high/low
            if mqtt_lib.button_mqtt.button_high == False:
                self.button_pause = False
            elif mqtt_lib.button_mqtt.button_high == True:
                self.button_pause = True

            # set progress
            music_progress = (((pygame.mixer.music.get_pos() / 1000.0) / self.song_length_seconds) * 100 )
            progress_bar.set_progress(music_progress)

            clock.tick(fps)

    def __calc_points(self, action_input_result):
        if action_input_result == SUCCESS:
            globals.points += 1
        elif action_input_result == TOO_EARLY or action_input_result == WRONG_KEY or action_input_result == WRONG_LANE:
            # allow players to try again as long as the thing is not gone yet
            # no point deduction for too early or wrong motion
            globals.points -= 0

    # function that helps print aligned to center
    # params:
    #   font
    #   Text object
    #   center is the desired tuple (x,y) you want text to be centered at
    #   color is color of text
    # returns you the thing you can use to print and its corresponding centered rect around center
    # e.g., you can just screen.blit(ret1, ret2)
    def __clean_print(self, font, Text, center, color=(0,0,0)):
        print_text = font.render(Text.text, True, color)
        print_text_rect = print_text.get_rect()
        print_text_rect.center = center
        return(print_text, print_text_rect)

    # parse the voice_message received from voice mqtt and set flags accordingly
    def __interpret_voice_recog(self, voice_message):
        if (voice_message == "pause"):
            self.pause = not self.pause
        elif (voice_message == "quit"):
            self.running = False
        elif (voice_message == "continue"):
            self.pause = False
        elif (voice_message == "start"):
            self.start_game = True

    def __game_over_cleanup(self):
        globals.points = 0
        globals.action_input_result_text = Text(text= "Good Luck!", rect=(SCREEN_WIDTH - (SCREEN_WIDTH/5) + 15, 20))
        globals.points_text = Text(text= "Points: 0", rect= (SCREEN_WIDTH - (SCREEN_WIDTH/8), 70))

    # loads music and bpm from song_title passed-in param
    def __load_music(self, song_title):
        if song_title[0] == 'A':
            pygame.mixer.music.load("music/songs/Black_Eyed_Peas--I_Gotta_Feeling--128bpm.wav")
            self.bpm = 128
            self.song_length_seconds = 290
        elif song_title[0] == 'B':
            pygame.mixer.music.load("music/songs/Ethel_Cain--American_Teenager--120bpm.wav")
            self.bpm = 120
            self.song_length_seconds = 260
        elif song_title[0] == 'C':
            pygame.mixer.music.load("music/songs/Gotye--Somebody_That_I_Used_to_Know--129bpm.wav")
            self.bpm = 129
            self.song_length_seconds = 246
        elif song_title[0] == 'D':
            pygame.mixer.music.load("music/songs/Taylor_Swift--You_Belong_With_Me--130bpm.wav")
            self.bpm = 130
            self.song_length_seconds = 233
        elif song_title[0] == 'E':
            pygame.mixer.music.load("music/songs/The_Beatles--All_You_Need_Is_Love--103bpm.wav")
            self.bpm = 103
            self.song_length_seconds = 232
        elif song_title[0] == 'F':
            pygame.mixer.music.load("music/songs/The_Beatles--While_My_Guitar_Gently_Weeps--115bpm.wav")
            self.bpm = 115
            self.song_length_seconds = 285
        else:
            pygame.mixer.music.load("music/songs/Taylor_Swift--You_Belong_With_Me--130bpm.wav")
            self.bpm = 130
            self.song_length_seconds = 233
        pygame.mixer.music.set_volume(0.5)