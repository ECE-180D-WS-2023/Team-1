import time
#import keyboard
import pygame
import paho.mqtt.client as mqtt
from menu import mqtt_lib
# import mqtt_lib
# from menu.mqtt_lib import SpeechFlags, MenuSpeechListener
import re

# song names
song_dict = {
    'A': "I Gotta Feeling", 
    'B': 'American Teenager',
    'C': 'Somebody That I Used To Know',
    'D': 'You Belong With Me',
    'E': 'All You Need Is Love',
    'F': 'While My Guitar Gently Weeps'}

my_pink = (242, 124, 201)

class Button:
    def __init__(self, text, x_pos, y_pos, enabled, screen, x_size = 300, y_size=40, toggle = True, song = False, clickable = True, color = my_pink):
        self.text = text
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.enabled = enabled
        self.screen = screen
        self.x_size = x_size
        self.y_size= y_size
        self.toggle = toggle
        self.song = song
        self.clickable = clickable
        self.color = color
        #self.draw()

    def draw(self):
        # could change size or add it to parameters later
        if not self.enabled:
            return
        font = pygame.font.Font('fonts/JMHTypewriter.ttf', 20)
        button_text = font.render(self.text, True, 'black')
        button_rect = pygame.rect.Rect((self.x_pos, self.y_pos), (self.x_size, self.y_size))
        if self.check_hover():
            pygame.draw.rect(self.screen, 'purple', button_rect, 0, 5)
        else:
            pygame.draw.rect(self.screen, self.color, button_rect, 0 , 5)
        # add outline to button
        pygame.draw.rect(self.screen, 'black', button_rect, 2, 5)
        if self.song:
            self.screen.blit(button_text, (self.x_pos+15, self.y_pos+10))
        else:
            self.screen.blit(button_text, (self.x_pos+(self.x_size/4.2), self.y_pos+(self.y_size/4)))
    
    def draw_toggle(self):
        if not self.enabled:
            return
        font = pygame.font.Font('fonts/JMHTypewriter.ttf', 20)
        option0_text = font.render(self.text[0], True, 'black')
        option1_text = font.render(self.text[1], True, 'black')
        option0_rect = pygame.rect.Rect((self.x_pos, self.y_pos), (145, 40))
        option1_rect = pygame.rect.Rect((self.x_pos + 150, self.y_pos), (145, 40))
        
        if self.toggle:
            pygame.draw.rect(self.screen, 'light blue', option0_rect, 0, 5)
            pygame.draw.rect(self.screen, 'pink', option1_rect, 0, 5)
            if self.check_toggle_hover(option1_rect):
                pygame.draw.rect(self.screen, 'purple', option1_rect, 0, 5)
        else:
            pygame.draw.rect(self.screen, 'pink', option0_rect, 0, 5)
            pygame.draw.rect(self.screen, 'light blue', option1_rect, 0, 5)
            if self.check_toggle_hover(option0_rect):
                pygame.draw.rect(self.screen, 'purple', option0_rect, 0, 5)
        # add outline to button
        pygame.draw.rect(self.screen, 'black', option0_rect, 2, 5)
        pygame.draw.rect(self.screen, 'black', option1_rect, 2, 5)
        self.screen.blit(option0_text, (self.x_pos+20, self.y_pos+10))
        self.screen.blit(option1_text, (self.x_pos+170, self.y_pos+10))

    # checks if button has been clicked
    def check_click(self):
        if not self.enabled:
            return
        if not self.clickable:
            return
        mouse_pos = pygame.mouse.get_pos()
        left_click = pygame.mouse.get_pressed()[0]
        button_rect = pygame.rect.Rect((self.x_pos, self.y_pos), (300, 40))
        if left_click and button_rect.collidepoint(mouse_pos) and self.enabled:
            return True
        else:
            return False
    
    def check_toggle_click(self):
        if not self.enabled:
            return
        mouse_pos = pygame.mouse.get_pos()
        left_click = pygame.mouse.get_pressed()[0]
        if self.toggle:
            x = self.x_pos + 150
        else:
            x = self.x_pos
        opt_rect = pygame.rect.Rect((x, self.y_pos), (145, 40))
        if left_click and opt_rect.collidepoint(mouse_pos) and self.enabled:
            return True
        else:
            return False

    def check_hover(self):
        if not self.clickable:
            return
        mouse_pos = pygame.mouse.get_pos()
        button_rect = pygame.rect.Rect((self.x_pos, self.y_pos), (self.x_size, self.y_size))
        if button_rect.collidepoint(mouse_pos) and self.enabled:
            return True
        else:
            return False
        
    def check_toggle_hover(self, button_rect):
        mouse_pos = pygame.mouse.get_pos()
        if button_rect.collidepoint(mouse_pos) and self.enabled:
            return True
        else:
            return False

class Menu():
    def __init__(self):
        self.t1_flags = mqtt_lib.SpeechFlags()
        self.t1_listener = mqtt_lib.MenuSpeechListener(self.t1_flags, "EECE180/Team1/speech")

        self.t2_flags = mqtt_lib.SpeechFlags()
        self.t2_listener = mqtt_lib.MenuSpeechListener(self.t2_flags, "EECE180/Team2/speech")

        self.team = 1 
        self.speech_flags = self.t1_flags
    
    def update_team_num(self, team_num):
        if team_num == 1:
            self.speech_flags = self.t1_flags
        elif team_num == 2: 
            self.speech_flags = self.t2_flags
        else:
            print("ERROR: Incorrect team_num")
            return

        self.team = team_num

    def draw_text(self, screen, text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        screen.blit(img, (x, y))

    def draw_background(self, screen):
        screen.fill((255, 255, 255))

    def button_apply(self, flag):
        if flag:
            return True
    
    def parse_lobbies(self, msg):
        # menu sends "LLR" for lobby list request
        # server receives this, then publishes lobby list
        # when LLR global = True, then 
        lobbies = []
        if msg == "" or msg == "Z" or msg == "Z,":
            return lobbies
        msg = msg[2:]
        lobby_list = msg.split(',')
        for item in lobby_list:
            lobbies.append((item[0], item[1]))
        return lobbies

    def start(self):
        # initializing the constructor 
        pygame.init()

        #team1 bool
        team1 = False

        #initializing mqtt client for voice recognition
        menu_mqtt_client = mqtt.Client()
        menu_mqtt_client.on_connect = self.speech_flags_on_connect
        menu_mqtt_client.on_disconnect = self.speech_flags_on_disconnect
        menu_mqtt_client.on_message = self.speech_flags_on_message
        menu_mqtt_client.connect_async('mqtt.eclipseprojects.io')
        menu_mqtt_client.loop_start()

        remote_client = mqtt.Client() 
        remote_client.on_connect = mqtt_lib.server_on_connect
        remote_client.on_disconnect = mqtt_lib.server_on_disconnect
        remote_client.on_message = mqtt_lib.server_on_message
        remote_client.connect_async('mqtt.eclipseprojects.io')
        remote_client.loop_start()

        res = (800,600) # screen resolution
        screen = pygame.display.set_mode(res) # opens up a window 
        smallfont = pygame.font.Font('fonts/JMHTypewriter.ttf', 35)
        bg = pygame.image.load("sprites/background.png").convert_alpha()
        menu_screen = True # start on menu screen
        settings_screen = False
        tutorial_screen = False
        song_screen = False
        lobby_screen = False
        waiting_room_screen = False
        open_lobby_screen = False
        song_letter = 'A'
        
        multi_color = (229, 152, 245)
        quit_color = (173, 152, 245)

        # define buttons
        start_button = Button('Start!', 250, 220, True, screen)
        settings_button = Button('Settings', 250, 270, True, screen)
        tutorial_button = Button('Tutorial', 250, 320, True, screen)
        quit_button = Button('Quit', 250, 420, True, screen, color = quit_color)
        remote_button = Button('Multiplayer', 250, 370, True, screen, color = multi_color)

        # remote_button = Button(remote_text, 250, 270, False, screen)
        player_text = ['One Player', 'Two Player']
        player_button = Button(player_text, 250, 320, False, screen)
        back_button = Button('Return', 250, 370, False, screen)

        team_id_text = ['Team A', 'Team B']
        team_id_button = Button(team_id_text, 250, 270, False, screen)

        # team one buttons
        # upon clicking create lobby button, we go to song selection screen
        create_lobby_button = Button('Create Lobby', 250, 440, False, screen)
        # after selecting a song, team 1 is now ready --> button says "waiting for team two to join"
        # until team 2 joins
        # join existing lobby --> 
        team1_status = Button('T1 Ready', 150, 300, False, screen, x_size = 200, y_size = 40, clickable = False)
        team2_status = Button('Waiting for T2...', 500, 300, False, screen, x_size = 200, y_size = 40, clickable = False, song = True)

        play_button = Button('Play', 400, 300, False, screen, x_size = 80, y_size = 40)
        # join_open_lobby = Button('Join Open Lobby', 250, 270, False, screen)

        # lobby buttons
        lobby1_button = Button("Lobby A", 150, 120, False, screen, x_size=500, song=True)
        lobby2_button = Button("Lobby B", 150, 170, False, screen, x_size=500, song=True)
        lobby3_button = Button("Lobby C", 150, 220, False, screen, x_size=500, song=True)
        lobby4_button = Button("Lobby D", 150, 270, False, screen, x_size=500, song=True)
        lobby5_button = Button("Lobby E", 150, 320, False, screen, x_size=500, song=True)
        lobby6_button = Button("Lobby F", 150, 370, False, screen, x_size=500, song=True)
        lobby_display = Button("", 150, 120, False, screen, x_size = 500, song=True, clickable=False)
        
        lobbies = []
        lobbies_buttons = []
        lobbies_buttons.append(lobby1_button)
        lobbies_buttons.append(lobby2_button)
        lobbies_buttons.append(lobby3_button)
        lobbies_buttons.append(lobby4_button)
        lobbies_buttons.append(lobby5_button)
        lobbies_buttons.append(lobby6_button)
        

        # song buttons
        song1_button = Button("A: I Gotta Feeling - Black Eyes Peas", 150, 120, False, screen, x_size=550, song=True)
        song2_button = Button("B: American Teenager - Ethel Cain", 150, 170, False, screen, x_size=550, song=True)
        song3_button = Button("C: Somebody That I Used To Know - Gotye", 150, 220, False, screen, x_size=550, song=True)
        song4_button = Button("D: You Belong With Me - Taylor Swift", 150, 270, False, screen, x_size=550, song=True)
        song5_button = Button("E: All You Need Is Love - The Beatles", 150, 320, False, screen, x_size=550, song = True)
        song6_button = Button("F: While My Guitar Gently Weeps - The Beatles", 150, 370, False, screen, x_size=550, song = True)
        song_back_button = Button("          Return", 150, 420, False, screen, x_size = 550)
        songs = []
        songs.append(song1_button)
        songs.append(song2_button)
        songs.append(song3_button)
        songs.append(song4_button)
        songs.append(song5_button)
        songs.append(song6_button)
        multi = False
        player_num = 1
        TEAM_ID = 1

        MESSAGE = pygame.USEREVENT + 1
        MESSAGE_REMOTE = pygame.USEREVENT + 2

        title_font = pygame.font.Font('fonts/JMHTypewriter.ttf', 48)
        title_text = title_font.render("Just Guitar Ninja Dance", True, (0,0,0))
        title_rect = title_text.get_rect()
        title_rect.center = (400, 600-7*600/8)

        song_text = 'a' 
        msg = ''

        def clear_flags():
            # set all flags to false
            self.speech_flags.QUIT_CLICK = False
            self.speech_flags.RETURN_CLICK = False
            self.speech_flags.MESSAGE_RECEIVED = False
            mqtt_lib.server_mqtt.MQTT_TEAM2_READY = False
            mqtt_lib.server_mqtt.MQTT_TEAM1_READY = False
            mqtt_lib.server_mqtt.MQTT_RECEIVED = False
            self.speech_flags.CREATE_CLICK = False
            self.speech_flags.MQTT_CLOSE_LOBBIES = False

        def clear_letters():
            # set all flags to false
            self.speech_flags.SONG_A = False
            self.speech_flags.SONG_B = False
            self.speech_flags.SONG_C = False
            self.speech_flags.SONG_D = False
            self.speech_flags.SONG_E = False
            self.speech_flags.SONG_F = False
            
        clear_flags()
        clear_letters()

        while True: 
            # global flags
            quit_click = self.speech_flags.QUIT_CLICK 
            return_click = self.speech_flags.RETURN_CLICK
            message_received = self.speech_flags.MESSAGE_RECEIVED
            mqtt_lobbies_list = mqtt_lib.server_mqtt.MQTT_LOBBIES
            mqtt_team2_ready = mqtt_lib.server_mqtt.MQTT_TEAM2_READY
            mqtt_team1_ready = mqtt_lib.server_mqtt.MQTT_TEAM1_READY
            mqtt_remote_received = mqtt_lib.server_mqtt.MQTT_RECEIVED
            create_click = self.speech_flags.CREATE_CLICK
            mqtt_update_lobbies = mqtt_lib.server_mqtt.MQTT_UPDATE_LOBBIES

            tutorial = False

            # display the background
            screen.blit(bg, (0,0,800,600))
            screen.blit(title_text, title_rect)

            start_button.draw()
            settings_button.draw()
            tutorial_button.draw()
            quit_button.draw()
            remote_button.draw()

            # remote_button.draw_toggle()
            player_button.draw_toggle()
            back_button.draw()
            team_id_button.draw_toggle()
            lobby_display.draw()
            
            create_lobby_button.draw()
            team1_status.draw()
            team2_status.draw()
            play_button.draw()


            for song in songs:
                song.draw()
            
            song_back_button.draw()

            for lobby in lobbies_buttons:
                lobby.draw()
            
    
            for ev in pygame.event.get(): 
                
                if ev.type == pygame.QUIT or quit_click: 
                    quit_click = False
                    pygame.quit() 
                    
                #checks if a mouse is clicked or message was received
                if ev.type == pygame.MOUSEBUTTONDOWN or ev.type == MESSAGE:
                    if menu_screen:
                        start_click = self.speech_flags.START_CLICK # ga
                        settings_click = self.speech_flags.SETTINGS_CLICK # sc
                        tutorial_click = self.speech_flags.TUTORIAL_CLICK # tc  
                        multi_click = self.speech_flags.MULTI_TEAM_CLICK
                        if start_button.check_click() or start_click:
                            #TODO send any flags to game here
                            self.speech_flags.START_CLICK = False
                            song_screen = True
                            start_button.enabled = False
                            settings_button.enabled = False
                            tutorial_button.enabled = False
                            quit_button.enabled = False
                            remote_button.enabled = False
                            for song in songs:
                                song.enabled = True
                            song_back_button.enabled = True
                            time.sleep(0.1)
                            break
                        elif quit_button.check_click() or quit_click:
                            self.speech_flags.QUIT_CLICK = False
                            pygame.quit()
                            exit() 
                        elif tutorial_button.check_click() or tutorial_click:
                            self.speech_flags.TUTORIAL_CLICK = False
                            tutorial_screen = True
                            menu_screen = False
                            # toggle buttons
                            start_button.enabled = False
                            settings_button.enabled = False
                            tutorial_button.enabled = False
                            quit_button.enabled = False
                            back_button.enabled = True
                            tutorial = True
                            team1 = True
                            return [multi, player_num, song1_button.text, tutorial, team1, TEAM_ID]
                            #break
                        elif settings_button.check_click() or settings_click:
                            self.speech_flags.SETTINGS_CLICK = False
                            settings_screen = True
                            menu_screen = False
                            # toggle buttons
                            start_button.enabled = False
                            settings_button.enabled = False
                            tutorial_button.enabled = False
                            quit_button.enabled = False
                            # remote_button.enabled = True
                            player_button.enabled = True
                            back_button.enabled = True
                            team_id_button.enabled = True
                            remote_button.enabled = False
                            self.speech_flags.ONE_PLAYER_CLICK= False
                            self.speech_flags.TWO_PLAYER_CLICK= False
                            self.speech_flags.TEAM_A_CLICK= False
                            self.speech_flags.TEAM_B_CLICK= False
                            clear_letters()
                            break
                        elif remote_button.check_click() or multi_click:
                            self.speech_flags.MULTI_TEAM_CLICK = False
                            lobby_screen = True
                            menu_screen = False
                            #toggle buttons
                            start_button.enabled = False
                            settings_button.enabled = False
                            tutorial_button.enabled = False
                            quit_button.enabled = False
                            remote_button.enabled = False
                            create_lobby_button.enabled = True
                            back_button.enabled = True
                            back_button.x_pos = 250
                            back_button.y_pos = 490
                            multi = True
                            remote_client.publish("ECE180/remote", "LLR", qos=1)
                            lobbies = self.parse_lobbies(mqtt_lobbies_list)
                            clear_letters()
                            # loop through current lobbies
                            # for each lobby, enable a button in lobby list
                                # set that button's text to 
                                # song name + # of players from lobby[0] and lobby[1]
                            # for song in songs:
                            #     song.color = my_pink
                            for lobby in lobbies:
                                lobby_text = lobby[0] + " - " + song_dict[lobby[0]] + ", #Players = " + lobby[1]
                                dark_pink = (173, 121, 155)
                                if lobby[0] == 'A':
                                    lobbies_buttons[0].enabled = True
                                    lobbies_buttons[0].text = lobby_text
                                    song1_button.color = dark_pink
                                    song1_button.clickable = False
                                if lobby[0] == 'B':
                                    lobbies_buttons[1].enabled = True
                                    lobbies_buttons[1].text = lobby_text
                                    song2_button.color = dark_pink
                                    song2_button.clickable = False
                                if lobby[0] == 'C':
                                    lobbies_buttons[2].enabled = True
                                    lobbies_buttons[2].text = lobby_text
                                    song3_button.color = dark_pink
                                    song3_button.clickable = False
                                if lobby[0] == 'D':
                                    lobbies_buttons[3].enabled = True
                                    lobbies_buttons[3].text = lobby_text
                                    song4_button.color = dark_pink
                                    song4_button.clickable = False
                                if lobby[0] == 'E':
                                    lobbies_buttons[4].enabled = True
                                    lobbies_buttons[4].text = lobby_text
                                    song5_button.color = dark_pink
                                    song5_button.clickable = False
                                if lobby[0] == 'F':
                                    lobbies_buttons[5].enabled = True
                                    lobbies_buttons[5].text = lobby_text
                                    song6_button.color = dark_pink
                                    song6_button.clickable = False
                                player_num = int(lobby[1])
                                # BEEP
                            break
                        
                    if settings_screen:
                        team_a_click = self.speech_flags.SONG_A
                        team_b_click = self.speech_flags.SONG_B
                        one_player_click = self.speech_flags.ONE_PLAYER_CLICK # 1p
                        two_player_click = self.speech_flags.TWO_PLAYER_CLICK # 2p
                        if back_button.check_click() or return_click: # TODO ADD FLAG
                            self.speech_flags.RETURN_CLICK = False
                            menu_screen = True
                            settings_screen = False
                            player_button.enabled = False
                            team_id_button.enabled = False
                            back_button.enabled = False
                            start_button.enabled = True
                            settings_button.enabled = True
                            tutorial_button.enabled = True
                            quit_button.enabled = True
                            remote_button.enabled = True
                            time.sleep(0.10)
                            break
                        if player_button.check_toggle_click():
                            player_button.toggle = not player_button.toggle
                            if player_num == 1:
                                player_num = 2
                            elif player_num == 2:
                                player_num = 1
                        if team_id_button.check_toggle_click():
                            team_id_button.toggle = not team_id_button.toggle
                            if TEAM_ID == 1:
                                TEAM_ID = 2
                            elif TEAM_ID == 2:
                                TEAM_ID = 1
                        elif one_player_click:
                            self.speech_flags.ONE_PLAYER_CLICK= False
                            player_button.toggle = not player_button.toggle
                            player_num = 1
                        elif two_player_click:
                            player_button.toggle = not player_button.toggle
                            self.speech_flags.TWO_PLAYER_CLICK= False
                            player_num = 2
                        elif team_a_click:
                            self.update_team_num(1)
                            team_id_button.toggle = not team_id_button.toggle
                            self.speech_flags.SONG_A= False
                            TEAM_ID = 1
                        elif team_b_click:
                            self.update_team_num(2)
                            team_id_button.toggle = not team_id_button.toggle
                            self.speech_flags.SONG_B= False
                            TEAM_ID = 2
                    if song_screen:
                        song_a = self.speech_flags.SONG_A
                        song_b = self.speech_flags.SONG_B
                        song_c = self.speech_flags.SONG_C
                        song_d = self.speech_flags.SONG_D
                        song_e = self.speech_flags.SONG_E
                        song_f = self.speech_flags.SONG_F
                        tutorial = False
                        if not multi:
                            for song in songs:
                                song.color = my_pink
                                song.clickable = True
                        elif multi:
                            for song in songs:
                                if not song.clickable:
                                    song.color = dark_pink
                        if song_back_button.check_click() or return_click: 
                            if multi:
                                multi = False
                            self.speech_flags.RETURN_CLICK = False
                            menu_screen = True
                            song_screen = False
                            # toggle buttons
                            start_button.enabled = True
                            settings_button.enabled = True
                            tutorial_button.enabled = True
                            quit_button.enabled = True
                            remote_button.enabled = True
                            for song in songs:
                                song.enabled = False
                            song_back_button.enabled = False
                            break
                        elif song1_button.check_click() or song_a:
                            self.speech_flags.SONG_A = False
                            team1 = True
                            return [multi, player_num, song1_button.text, tutorial, team1, TEAM_ID]
                        elif song2_button.check_click() or song_b:
                            self.speech_flags.SONG_B = False
                            team1 = True
                            return [multi, player_num, song2_button.text, tutorial, team1, TEAM_ID]
                        elif song3_button.check_click() or song_c:
                            self.speech_flags.SONG_C = False
                            team1 = True
                            return [multi, player_num, song3_button.text, tutorial, team1, TEAM_ID]
                        elif song4_button.check_click() or song_d:
                            self.speech_flags.SONG_D = False
                            team1 = True
                            return [multi, player_num, song4_button.text, tutorial, team1, TEAM_ID]
                        elif song5_button.check_click() or song_e:
                            self.speech_flags.SONG_E = False
                            team1 = True
                            return [multi, player_num, song5_button.text, tutorial, team1, TEAM_ID]
                        elif song6_button.check_click() or song_f:
                            self.speech_flags.SONG_F = False
                            team1 = True
                            return [multi, player_num, song6_button.text, tutorial, team1, TEAM_ID]
                    if lobby_screen:
                        mqtt_lobbies_list = mqtt_lib.server_mqtt.MQTT_LOBBIES
                        song_a = self.speech_flags.SONG_A
                        song_b = self.speech_flags.SONG_B
                        song_c = self.speech_flags.SONG_C
                        song_d = self.speech_flags.SONG_D
                        song_e = self.speech_flags.SONG_E
                        song_f = self.speech_flags.SONG_F
                        lobbies = self.parse_lobbies(mqtt_lobbies_list)
                        for lobby_button in lobbies_buttons:
                            lobby = ''
                            if song_a:
                                self.speech_flags.SONG_A = False
                                lobby = 'A'
                            if song_b:
                                self.speech_flags.SONG_B = False
                                lobby =  'B'
                            if song_c:
                                self.speech_flags.SONG_C = False
                                lobby = 'C'
                            if song_d:
                                self.speech_flags.SONG_D = False
                                lobby = 'D'
                            if song_e:
                                self.speech_flags.SONG_E = False
                                lobby = 'E'
                            if song_f:
                                self.speech_flags.SONG_F = False
                                lobby = 'F'
                            lobby_speech = False
                            if lobby == lobby_button.text[0]:
                                lobby_speech = True
                            if lobby_button.enabled and (lobby_button.check_click() or lobby_speech):
                                waiting_room_screen = True
                                lobby_screen = False
                                back_button.song = True
                                back_button.text = "   Return to main menu"
                                team2_status.text = "T2 Ready"
                                team1_status.enabled = True
                                team2_status.enabled = True
                                i = 0
                                for button in lobbies_buttons:
                                    button.enabled = False
                                    i += 1

                                create_lobby_button.enabled = False
                                remote_client.publish("ECE180/remote", "T2_READY", qos=1)
                                song_text = lobby_button.text
                                lobby_display.text = lobby_button.text
                                lobby_display.enabled = True
                                team1 = False
                                break
                        if back_button.check_click() or return_click:
                            self.speech_flags.RETURN_CLICK = False
                            menu_screen = True
                            lobby_screen = False
                            # toggle buttons
                            start_button.enabled = True
                            settings_button.enabled = True
                            tutorial_button.enabled = True
                            quit_button.enabled = True
                            remote_button.enabled = True
                            back_button.enabled = False
                            team1_status.enabled = False
                            team2_status.enabled = False
                            create_lobby_button.enabled = False
                            lobby_display.enabled = False
                            i = 0
                            for lobby in lobbies_buttons:
                                lobbies_buttons[i].enabled = False
                                i += 1
                            time.sleep(0.20)
                            break
                        if create_lobby_button.check_click() or create_click:
                            self.speech_flags.CREATE_CLICK = False
                            open_lobby_screen = True
                            lobby_screen = False
                            back_button.enabled = False
                            quit_button.enabled = False
                            song_back_button.enabled = True
                            create_lobby_button.enabled = False
                            team1 = True
                            for song in songs:
                                song.enabled = True
                                if not song.clickable:
                                    song.color = dark_pink
                            i = 0
                            for lobby in lobbies_buttons:
                                lobbies_buttons[i].enabled = False
                                i += 1
                            time.sleep(0.5)
                            break
                        if mqtt_update_lobbies and not waiting_room_screen:
                            lobbies = self.parse_lobbies(mqtt_lobbies_list)
                            for lobby in lobbies:
                                dark_pink = (173, 121, 155)
                                lobby_text = lobby[0] + " - " + song_dict[lobby[0]] + ", #Players = " + lobby[1]
                                if lobby[0] == 'A':
                                    lobbies_buttons[0].enabled = True
                                    lobbies_buttons[0].text = lobby_text
                                    song1_button.color = dark_pink
                                    song1_button.clickable = False
                                if lobby[0] == 'B':
                                    lobbies_buttons[1].enabled = True
                                    lobbies_buttons[1].text = lobby_text
                                    song2_button.color = dark_pink
                                    song2_button.clickable = False
                                if lobby[0] == 'C':
                                    lobbies_buttons[2].enabled = True
                                    lobbies_buttons[2].text = lobby_text
                                    song3_button.color = dark_pink
                                    song3_button.clickable = False
                                if lobby[0] == 'D':
                                    lobbies_buttons[3].enabled = True
                                    lobbies_buttons[3].text = lobby_text
                                    song4_button.color = dark_pink
                                    song4_button.clickable = False
                                if lobby[0] == 'E':
                                    lobbies_buttons[4].enabled = True
                                    lobbies_buttons[4].text = lobby_text
                                    song5_button.color = dark_pink
                                    song5_button.clickable = False
                                if lobby[0] == 'F':
                                    lobbies_buttons[5].enabled = True
                                    lobbies_buttons[5].text = lobby_text
                                    song6_button.color = dark_pink
                                    song6_button.clickable = False
                                player_num = int(lobby[1])
                                # BEEP
                            mqtt_lib.server_mqtt.MQTT_RECEIVED = False
                            break
                    if open_lobby_screen:
                        create_click = self.speech_flags.CREATE_CLICK
                        song_a = self.speech_flags.SONG_A
                        song_b = self.speech_flags.SONG_B
                        song_c = self.speech_flags.SONG_C
                        song_d = self.speech_flags.SONG_D
                        song_e = self.speech_flags.SONG_E
                        song_f = self.speech_flags.SONG_F
                        tutorial = False
                        team1 = True
                        if song_back_button.check_click() or return_click: 
                            if multi:
                                multi = False
                            self.speech_flags.RETURN_CLICK = False
                            menu_screen = True
                            song_screen = False
                            # toggle buttons
                            start_button.enabled = True
                            settings_button.enabled = True
                            tutorial_button.enabled = True
                            quit_button.enabled = True
                            remote_button.enabled = True
                            team1 = False
                            for song in songs:
                                song.enabled = False
                            song_back_button.enabled = False
                            time.sleep(0.25)
                            break
                        elif song1_button.check_click() or song_a:
                            self.speech_flags.SONG_A = False
                            # launch lobby into waiting room
                            waiting_room_screen = True
                            # toggle buttons
                            for song in songs:
                                song.enabled = False
                            song_back_button.enabled = False
                            team1_status.enabled = True
                            team2_status.enabled = True
                            back_button.song = True
                            back_button.text = "   Return to main menu"
                            back_button.enabled = True
                            lobby_text = song_dict['A'] + ", #Players = " + str(player_num)
                            lobby_display.text = lobby_text
                            lobby_display.enabled = True
                            song_text = 'A'
                            msg = "A" + str(player_num)
                            remote_client.publish("ECE180/remote", msg, qos=1)
                            break
                        elif song2_button.check_click() or song_b:
                            self.speech_flags.SONG_B = False
                            # launch lobby into waiting room
                            waiting_room_screen = True
                            # toggle buttons
                            for song in songs:
                                song.enabled = False
                            song_back_button.enabled = False
                            team1_status.enabled = True
                            team2_status.enabled = True
                            back_button.song = True
                            back_button.text =  "   Return to main menu"
                            back_button.enabled = True
                            lobby_text = song_dict['B'] + ", #Players = " + str(player_num)
                            lobby_display.text = lobby_text
                            lobby_display.enabled = True
                            song_text = 'B'
                            msg = "B" + str(player_num)
                            remote_client.publish("ECE180/remote", msg, qos=1)
                            break
                        elif song3_button.check_click() or song_c:
                            self.speech_flags.SONG_C = False
                            # launch lobby into waiting room
                            waiting_room_screen = True
                            # toggle buttons
                            for song in songs:
                                song.enabled = False
                            song_back_button.enabled = False
                            team1_status.enabled = True
                            team2_status.enabled = True
                            back_button.song = True
                            back_button.text = "   Return to main menu"
                            back_button.enabled = True
                            song_text = 'C'
                            lobby_text = song_dict['C'] + ", #Players = " + str(player_num)
                            lobby_display.text = lobby_text
                            lobby_display.enabled = True
                            msg = "C" + str(player_num)
                            remote_client.publish("ECE180/remote", msg, qos=1)
                            break
                        elif song4_button.check_click() or song_d:
                            self.speech_flags.SONG_D = False
                            # launch lobby into waiting room
                            waiting_room_screen = True
                            # toggle buttons
                            for song in songs:
                                song.enabled = False
                            song_back_button.enabled = False
                            team1_status.enabled = True
                            team2_status.enabled = True
                            back_button.song = True
                            back_button.text = "   Return to main menu"
                            back_button.enabled = True
                            lobby_text = song_dict['D'] + ", #Players = " + str(player_num)
                            song_text = 'D'
                            lobby_display.text = lobby_text
                            lobby_display.enabled = True
                            msg = "D" + str(player_num)
                            remote_client.publish("ECE180/remote", msg, qos=1)
                            break
                        elif song5_button.check_click() or song_e:
                            self.speech_flags.SONG_E = False
                            waiting_room_screen = True
                            # toggle buttons
                            for song in songs:
                                song.enabled = False
                            song_back_button.enabled = False
                            team1_status.enabled = True
                            team2_status.enabled = True
                            back_button.song = True
                            back_button.text = "   Return to main menu"
                            back_button.enabled = True
                            lobby_text = song_dict['E'] + ", #Players = " + str(player_num)
                            song_text = 'E'
                            lobby_display.text = lobby_text
                            lobby_display.enabled = True
                            msg = "E" + str(player_num)
                            remote_client.publish("ECE180/remote", msg, qos=1)
                            break
                        elif song6_button.check_click() or song_f:
                            self.speech_flags.SONG_F = False
                            # launch lobby into waiting room
                            waiting_room_screen = True
                            # toggle buttons
                            for song in songs:
                                song.enabled = False
                            song_back_button.enabled = False
                            team1_status.enabled = True
                            team2_status.enabled = True
                            back_button.song = True
                            back_button.text = "   Return to main menu"
                            back_button.enabled = True
                            lobby_text = song_dict['F'] + ", #Players = " + str(player_num)
                            lobby_display.text = lobby_text
                            lobby_display.enabled = True
                            song_text = 'F'
                            msg = "F" + str(player_num)
                            remote_client.publish("ECE180/remote", msg, qos=1)
                            break
                    if waiting_room_screen:
                        if back_button.check_click() or return_click:
                            self.speech_flags.RETURN_CLICK = False
                            menu_screen = True
                            back_button.text = "Return"
                            back_button.song = False
                            waiting_room_screen = False
                            for lobby_button in lobbies_buttons:
                                lobby_button.enabled = False
                            # toggle buttons
                            back_button.enabled = False
                            team1_status.enabled = False
                            team2_status.enabled = False
                            remote_button.enabled = True
                            start_button.enabled = True
                            settings_button.enabled = True
                            tutorial_button.enabled = True
                            quit_button.enabled = True
                            lobby_display.enabled = False
                            quit_click = False
                            play_button.enabled = False
                            remove_lobby = "R" + song_text[0].capitalize() + str(player_num)
                            remote_client.publish("ECE180/remote", remove_lobby, qos=1)
                            print("waiting room removing lobby:" + remove_lobby)
                            time.sleep(0.15)
                            break
                        #if team1:
                        if team1 and play_button.check_click():
                            print("team 1 launching")
                            remote_client.publish("ECE180/remote", "T1_READY", qos=1)
                            remove_lobby = "R" + song_text[0].capitalize() + str(player_num)
                            remote_client.publish("ECE180/remote", remove_lobby, qos=1)
                            remote_client.publish("ECE180/remote", msg, qos=1)
                            return [multi, player_num, song_text, tutorial, team1, TEAM_ID]
                        elif team1 and mqtt_team2_ready:
                            team2_status.text = "T2 Ready"
                            play_button.enabled = True
                            break
                        # draw "waiting for team 2 to join" on play button
                            # when team 2 joins change to play button
                        # if team 2: 
                        if not team1 and mqtt_team1_ready:
                        # draw "waiting for both teams to press start"
                            print("team 2 launching")
                            return [multi, player_num, song_text, tutorial, team1, TEAM_ID]
                            # draw play button                    
                                                    
            if message_received:
                pygame.event.post(pygame.event.Event(MESSAGE))
                message_received = False
            if mqtt_remote_received:
                pygame.event.post(pygame.event.Event(MESSAGE))
                mqtt_remote_received = False
            # updates the frames of the game 
            pygame.display.update() 
