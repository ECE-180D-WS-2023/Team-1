import pygame
import paho.mqtt.client as mqtt
import logging
import random

from game.mqtt_lib import ButtonListener, LocalizationListener, IMUListener, SpeechListener

from .Note import Note, FadingNote, get_lowest_note, SUCCESS, TOO_EARLY, WRONG_KEY, WRONG_LANE
from .Settings import SCREEN_WIDTH, SCREEN_HEIGHT, HIT_ZONE_LOWER, HIT_ZONE_TEXT, HIGHLIGHT_COLOR, BACKGROUND_COLOR, PROG_COLOR, note_update_time
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
        # song length per team for remote play
        self.song_length_per_team = int(self.song_length_seconds/8)

        # notes list
        self.notes = pygame.sprite.Group()
        self.red_notes = pygame.sprite.Group()
        self.blue_notes = pygame.sprite.Group()
        self.fading_notes = pygame.sprite.Group()

        # mqtt listeners
        self.listeners = {
            'team1': {
                'button_listener': ButtonListener(),
                'speech_listener': SpeechListener(),
                'localization_listener': LocalizationListener(),
                'imu_listener': IMUListener()
            },
            'team2': {
                'button_listener': ButtonListener(),
                'speech_listener': SpeechListener(),
                'localization_listener': LocalizationListener(),
                'imu_listener': IMUListener()
            }
        }
        self.active_listeners = self.listeners['team1']
        self.active_team = 'team1'
        self.last_switch_time = 0
        self.my_team = 'team1'

        # store imu actions
        self.imu_action_1 = None
        self.imu_action_2 = None

        # list of texts and fonts
        self.hitzone_text = Text(text= "Hit-Zone", rect= (20, HIT_ZONE_TEXT))
        self.paused_text = Text(text="Paused", rect=(10, SCREEN_HEIGHT/3))
        self.start_game_text = Text(text="Press S To Start", rect=(10, SCREEN_HEIGHT/3))
        self.instruction_text = Text(text="", rect=(10, SCREEN_HEIGHT/3))
        self.result_font = pygame.font.Font('fonts/JMHTypewriter.ttf', RESULT_FONT_SIZE)
        self.hitzone_font = pygame.font.Font('fonts/JMHTypewriter.ttf', HITZONE_FONT_SIZE)
        self.paused_font = pygame.font.Font('fonts/JMHTypewriter.ttf', PAUSED_FONT_SIZE)
        self.points_font = pygame.font.Font('fonts/JMHTypewriter.ttf', RESULT_FONT_SIZE)

        # custom events for receiving imu action
        self.ACTION_1 = pygame.USEREVENT + 2 # for p1
        self.ACTION_2 = pygame.USEREVENT + 3 # for p2
        self.pause_button = pygame.image.load("sprites/pause_g38.png").convert_alpha()
        self.play_button = pygame.image.load("sprites/play_g38.png").convert_alpha()

    def tutorial(self, num_players=2): #tutorial mode of the game (Slow bpm to spawn notes)
        globals.NUM_PLAYERS = num_players
        # set bpm
        self.bpm = 10
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        logging.info(f"Tutorial: Starting {num_players}P tutorial with: Width:{SCREEN_WIDTH}, Height:{SCREEN_HEIGHT}")

        # Instantiate sprite groups
        players = pygame.sprite.Group()
        players.add(Player(1))
        if(num_players == 2):
            players.add(Player(2))

        # probably will eventually include other sprites like powerups or chars
        all_sprites = pygame.sprite.Group()

        # text for hitzone, for results, and points
        instructions = {
            'u':" lift UP when in hit-zone.",
            'f':" push FORWARD when in hit-zone.",
            'l':" swipe LEFT when in hit-zone.",
            'r':" swipe RIGHT when in hit-zone.",
            1 : "Move icon to falling note's lane &",
            2 : "Move icon to falling note's lane &",
        }

        SPAWNNOTE = pygame.USEREVENT + 1
        pygame.time.set_timer(SPAWNNOTE, int(0))
        note_spawn_speed_ms = ((1/self.bpm)*60)*1000

        last_note_update = pygame.time.get_ticks()

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

        self.running = True
        while (score < completed_score and self.running):
            for event in pygame.event.get():
                # check if q is pressed then leave
                if event.type == KEYDOWN:
                    self.__process_keydown(event.key)
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
                    self.instruction_text = Text(text=instructions[color_idx]+instructions[char_idx], rect=(10, SCREEN_HEIGHT/3))
                    new_note = Note(color=color_idx, lane=lane_idx, char=char_idx)
                    self.notes.add(new_note)
                    self.red_notes.add(new_note)
                    all_sprites.add(new_note)
                # if we receive some action from imu
                elif event.type == self.ACTION_1:
                    self.__process_action_event(1)
                # this should never be true in 1p bcus action_2 should never be raised
                elif event.type == self.ACTION_2:
                    self.__process_action_event(2)
            
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
                self.__check_and_process_imu_mqtt_received(num_players=num_players)
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
                    player.update_player_pos(player_num = 1, coords = self.active_listeners['localization_listener'].p1.coords)
                elif (player.player_num == 2):
                    player.update_player_pos(player_num = 2, coords = self.active_listeners['localization_listener'].p2.coords)

            # Fill the screen with background color
            screen.fill(BACKGROUND_COLOR)

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
            screen.blit(self.result_font.render(globals.action_input_result_text.text, True, (0,0,0)), globals.action_input_result_text.rect)
            
            # text for hitzone indicator
            screen.blit(self.hitzone_font.render(self.hitzone_text.text, True, (255,0,0), (255,255,102)), self.hitzone_text.rect)
            
            # text for pause
            if (self.pause or self.button_pause):
                print_paused, print_paused_rect = self.__clean_print(font=self.paused_font, Text=self.paused_text, center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                screen.blit(print_paused, print_paused_rect)
            elif (not self.start_game):
                print_start_game, print_start_game_rect = self.__clean_print(font=self.paused_font, Text=self.start_game_text, center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                screen.blit(print_start_game, print_start_game_rect)
                # do not allow the game to be paused while game has not started
                self.pause = False
            else:
                print_inst, print_inst_rect = self.__clean_print(font=self.result_font, Text=self.instruction_text, center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2), color=player_color, background=HIGHLIGHT_COLOR)
                screen.blit(print_inst, print_inst_rect)

            # Update the display
            pygame.display.flip()
        globals.points = 0
        self.start_game = False

    # FOR 2 PLAYER GAME, THE ONLY IF STATEMENTS ARE FOR
    # INITIALIZING THE SECOND PLAYER AND THE IF STATEMENT PROTECTING self.ACTION_2
    def start(self, num_players=2, song_title="A: ", remote_play=False, team_1=True):
        # setup global vars
        # set num players globally so Notes know to only create 1 color
        globals.NUM_PLAYERS = num_players

        # set active listeners based on team
        if (team_1 == True or remote_play == False):
            self.active_team = 'team1'
            self.my_team = 'team1'
        else:
            self.active_team = 'team2'
            self.my_team = 'team2'
        self.active_listeners = self.listeners[self.active_team]

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

        # instantiate sprite groups
        players = pygame.sprite.Group()
        players.add(Player(1))
        if(num_players == 2):
            players.add(Player(2))

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

        # custom note update per speed along with note fall speed
        last_note_update = pygame.time.get_ticks()

        # stores previous pause state to know whether we resumed or not to continue note generation
        prev_pause = False
        prev_start_game = False

        # Variable to keep the main loop running
        self.running = True
        while self.running:
            for event in pygame.event.get():
                # check if q is pressed then leave
                if event.type == KEYDOWN:
                    self.__process_keydown(event.key)
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
                elif event.type == self.ACTION_1:
                    self.__process_action_event(1)
                # this should never be true in 1p bcus action_2 should never be raised
                elif event.type == self.ACTION_2:
                    self.__process_action_event(2)

            # handle voice recognition stuff
            if self.active_listeners['speech_listener'].received:
                self.__interpret_voice_recog(self.active_listeners['speech_listener'].keyword)
                self.active_listeners['speech_listener'].debug_set_received(val=False)
            # handling pause -> unpause transition to resume note spawning timer
                # if we just started to pause, set note spawning timer to 0
                # if we just resumed the game, set note spawning timer back to normal
            if self.pause or self.button_pause:
                if prev_pause == False:
                    pygame.time.set_timer(SPAWNNOTE, 0)
                    pygame.mixer.music.pause()
                prev_pause = True
            # if BOTH pause and button_pause false
            else:
                if prev_pause == True:
                    start_note_spawn_delay = True
                    start_note_spawn_timestamp = pygame.time.get_ticks()
                    pygame.mixer.music.unpause()
                prev_pause = False
            # same with start_game to start the note timer and start music
            if self.start_game:
                if prev_start_game == False:
                    start_note_spawn_delay = True
                    start_note_spawn_timestamp = pygame.time.get_ticks()
                    pygame.mixer.music.play()

                    # used for remote play switching between teams
                    self.last_switch_time = 0
                prev_start_game = True


            # when pause game, also don't allow action to be read in and dont
            # let there be updated notes
            if self.start_game and not (self.pause or self.button_pause):
            # if action registered by imu, do the event notification and put the action into imu_action
            # when on_message is called, set some global variable imu_action_received_flag to True and set the action to imu_action
            # because the imu_mqtt runs in parallel, we want to do this flag true and false 
                self.__check_and_process_imu_mqtt_received(num_players=num_players)
                # update note positions
                if (pygame.time.get_ticks() - last_note_update > note_update_time):
                    #self.notes.update()
                    for note in self.notes:
                        result = note.update()
                        # need to subtract 1 from score
                        if result == -1 and self.active_team == self.my_team:
                            globals.points -= 1
                            globals.action_input_result_text.update(text="Missed!")
                    last_note_update = pygame.time.get_ticks()

            # update player location
            for player in players:
                if (player.player_num == 1):
                    player.update_player_pos(player_num = 1, coords = self.active_listeners['localization_listener'].p1.coords)
                elif (player.player_num == 2):
                    player.update_player_pos(player_num = 2, coords = self.active_listeners['localization_listener'].p2.coords)

            # check if there are any notes that need fading
            for note in self.notes:
                if note.fade:
                    fading_note = FadingNote(note)
                    self.fading_notes.add(fading_note)
                    note.fade = False
            # update fading notes animation
            self.fading_notes.update()

            # Fill the screen background
            screen.fill(BACKGROUND_COLOR)

            # draw progress bar
            progress_bar.draw(screen, outline_color=pygame.Color(128, 128, 128, 100), inner_color=PROG_COLOR, remote_play=remote_play)

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
            screen.blit(self.result_font.render(globals.action_input_result_text.text, True, (0,0,0)), globals.action_input_result_text.rect)
            
            # update text for points
            globals.points_text.update(text="Points: " + str(globals.points))
            # print points
            # screen.blit(self.points_font.render(globals.points_text.text, True, (0,0,0)), globals.points_text.rect)
            print_points, print_points_rect = self.__clean_print(font=self.points_font, Text=globals.points_text, center=globals.points_text.rect, color=(0,0,0), background=HIGHLIGHT_COLOR)
            screen.blit(print_points, print_points_rect)

            # text for hitzone indicator
            screen.blit(self.hitzone_font.render(self.hitzone_text.text, True, (255,0,0), (255,255,102)), self.hitzone_text.rect)
            # display hit zone
            # horizontal line to indicate hit zone
            pygame.draw.line(screen, (255, 0, 0), (0, HIT_ZONE_LOWER), (SCREEN_WIDTH, HIT_ZONE_LOWER))

            # if game hasnt started yet, set progress to 0 and display the startgame text
            if (not self.start_game):
                self.progress = 0
                
                print_start_game, print_start_game_rect = self.__clean_print(font=self.paused_font, Text=self.start_game_text, center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                screen.blit(print_start_game, print_start_game_rect)
                # do not allow the game to be paused while game has not started
                self.pause = False
                self.button_pause = False
            
            # text for pause
            if (self.pause or self.button_pause):
                screen.blit(self.play_button, (SCREEN_WIDTH-14*SCREEN_WIDTH/15, SCREEN_HEIGHT-14*SCREEN_HEIGHT/15 - 10))
                print_paused, print_paused_rect = self.__clean_print(font=self.paused_font, Text=self.paused_text, center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                screen.blit(print_paused, print_paused_rect)
            else:
                screen.blit(self.pause_button, (SCREEN_WIDTH-14*SCREEN_WIDTH/15, SCREEN_HEIGHT-14*SCREEN_HEIGHT/15 - 10))

            # Update the display
            pygame.display.flip()

            # if need delay before starting note spawn
            if (not self.pause and not self.button_pause):
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
            if self.active_listeners['button_listener'].button_high == False:
                self.button_pause = False
            elif self.active_listeners['button_listener'].button_high == True:
                self.button_pause = True

            # set progress
            music_progress = (((pygame.mixer.music.get_pos() / 1000.0) / self.song_length_seconds) * 100 )
            progress_bar.set_progress(music_progress)

            # calculate when to switch teams
            if (remote_play == True):
                if ((pygame.mixer.music.get_pos() / 1000.0) - self.last_switch_time) >= self.song_length_per_team:
                    # switch !!
                    if self.active_team == 'team1':
                        self.active_team = 'team2'
                    elif self.active_team == 'team2':
                        self.active_team = 'team1'
                    self.active_listeners = self.listeners[self.active_team]
                    self.last_switch_time = pygame.mixer.music.get_pos() / 1000.0

                    print("switched! active_team now: ", self.active_team)
            clock.tick(fps)

    def __calc_points(self, action_input_result):
        if (self.my_team == self.active_team):
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
    def __clean_print(self, font, Text, center, color=(0,0,0), background=None):
        if (background == None):
            print_text = font.render(Text.text, True, color)
        else:
            print_text = font.render(Text.text, True, color, background)
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
        globals.points_text = Text(text= "Points: 0", rect= (SCREEN_WIDTH - (SCREEN_WIDTH/8), 20))
        globals.action_input_result_text = Text(text= "Good Luck!", rect=(SCREEN_WIDTH-14*(SCREEN_WIDTH/15), 5))

    # loads music and bpm from song_title passed-in param
    def __load_music(self, song_title):
        if song_title[0] == 'A':
            pygame.mixer.music.load("music/songs/Black_Eyed_Peas--I_Gotta_Feeling--128bpm.wav")
            self.bpm = 128
            self.song_length_seconds = 290
            self.song_length_per_team = int(self.song_length_seconds/8)
        elif song_title[0] == 'B':
            pygame.mixer.music.load("music/songs/Ethel_Cain--American_Teenager--120bpm.wav")
            self.bpm = 120
            self.song_length_seconds = 260
            self.song_length_per_team = int(self.song_length_seconds/8)
        elif song_title[0] == 'C':
            pygame.mixer.music.load("music/songs/Gotye--Somebody_That_I_Used_to_Know--129bpm.wav")
            self.bpm = 129
            self.song_length_seconds = 246
            self.song_length_per_team = int(self.song_length_seconds/8)
        elif song_title[0] == 'D':
            pygame.mixer.music.load("music/songs/Taylor_Swift--You_Belong_With_Me--130bpm.wav")
            self.bpm = 130
            self.song_length_seconds = 233
            self.song_length_per_team = int(self.song_length_seconds/8)
        elif song_title[0] == 'E':
            pygame.mixer.music.load("music/songs/The_Beatles--All_You_Need_Is_Love--103bpm.wav")
            self.bpm = 103
            self.song_length_seconds = 232
            self.song_length_per_team = int(self.song_length_seconds/8)
        elif song_title[0] == 'F':
            pygame.mixer.music.load("music/songs/The_Beatles--While_My_Guitar_Gently_Weeps--115bpm.wav")
            self.bpm = 115
            self.song_length_seconds = 285
            self.song_length_per_team = int(self.song_length_seconds/8)
        else:
            pygame.mixer.music.load("music/songs/Taylor_Swift--You_Belong_With_Me--130bpm.wav")
            self.bpm = 130
            self.song_length_seconds = 233
            self.song_length_per_team = int(self.song_length_seconds/8)
        pygame.mixer.music.set_volume(0.5)

    # helper methods between tutorial and game
    # process when keystroke happens
    def __process_keydown(self, key_stroke):
        if key_stroke == K_q:
            self.running = False
        elif key_stroke == K_p:
            #self.pause = not self.pause
            self.active_listeners['speech_listener'].debug_set_received(True)
            self.active_listeners['speech_listener'].debug_set_msg("pause")
        elif key_stroke == K_s:
            self.start_game = True
        elif key_stroke == K_b:
            self.active_listeners['button_listener'].debug_button_set(val= not self.active_listeners['button_listener'].button_high)
        elif key_stroke == K_1 or key_stroke == K_2 or key_stroke == K_3 or key_stroke == K_4:
            if (key_stroke == K_1):
                self.active_listeners['localization_listener'].debug_set_location(player_num=1, val=1)
                self.active_listeners['localization_listener'].debug_set_coords(player_num=1, val=560)
            elif (key_stroke == K_2):
                self.active_listeners['localization_listener'].debug_set_location(player_num=1, val=2)
                self.active_listeners['localization_listener'].debug_set_coords(player_num=1, val=400)
            elif (key_stroke == K_3):
                self.active_listeners['localization_listener'].debug_set_location(player_num=1, val=3)
                self.active_listeners['localization_listener'].debug_set_coords(player_num=1, val=240)
            elif (key_stroke == K_4):
                self.active_listeners['localization_listener'].debug_set_location(player_num=1, val=4)
                self.active_listeners['localization_listener'].debug_set_coords(player_num=1, val=80)
        else:
            # calculate which note is the lowest and then process key press accordingly based
            # on that note's letter
            if (self.red_notes.sprites()):
                lowest_note = get_lowest_note(self.red_notes)
                if (lowest_note):
                    action_input_result = lowest_note.process_action_location(pygame.key.name(key_stroke), self.active_listeners['localization_listener'].p1.location, 1)
                    self.__calc_points(action_input_result)
                else:
                    action_input_result = "No Notes Yet!"
            else:
                action_input_result = "No Notes Yet!"
            globals.action_input_result_text.update(text=action_input_result)
        
    # process action events
        # player_action_num == which player did the action
    def __process_action_event(self, player_action_num):
        if (self.notes):
            lowest_note = get_lowest_note(self.notes)
            if (lowest_note):
            # process key works for now since it is just diff letters
                if player_action_num == 1:
                    action_input_result = lowest_note.process_action_location(self.imu_action_1, self.active_listeners['localization_listener'].p1.location, 1)
                else:
                    action_input_result = lowest_note.process_action_location(self.imu_action_2, self.active_listeners['localization_listener'].p2.location, 2)
                self.__calc_points(action_input_result)
            else:
                action_input_result = "No Notes Yet!"
        else:
            action_input_result = "No Notes Yet!"
        globals.action_input_result_text.update(text=action_input_result)

    def __check_and_process_imu_mqtt_received(self, num_players):
        if (self.active_listeners['imu_listener'].p1.received_action):
            pygame.event.post(pygame.event.Event(self.ACTION_1))
            self.imu_action_1 = self.active_listeners['imu_listener'].p1.action
            print("action received: ", self.imu_action_1)
            self.active_listeners['imu_listener'].debug_set_received(player_num=1, val=False)
        if (num_players == 2):
            if (self.active_listeners['imu_listener'].p2.received_action):
                pygame.event.post(pygame.event.Event(self.ACTION_2))
                self.imu_action_2 = self.active_listeners['imu_listener'].p2.action
                print("action received: ", self.imu_action_2)
                self.active_listeners['imu_listener'].debug_set_received(player_num=2, val=False)