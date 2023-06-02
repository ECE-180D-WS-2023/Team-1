import time
import keyboard
import pygame
import paho.mqtt.client as mqtt
from menu import mqtt_lib
import re




#TODO (spring quarter) 5/11
# menu should display "multiplayer" option
# upon clicking multiplayer --> enters screen with list of open lobbies (which have song title and # players associated with each lobby) and "create lobby" button at the bottom
# if they click create lobby, just instantly to new screen “select # players and song” – this can have like similar layout to settings and song selection merge the two or something
# Then create lobby button at the bottom
    # once “create new lobby” selected send information to the server about this created 
	# lobby
    	# the team that created the lobby becomes team 1
    	# lobby should display "team 1 connected, waiting for team 2" “lobby settings: ”
    # upon team 2 joining, should add "play" button 
        # could either team press play? Lets just make team 1 only able to select
# if they select an already existing lobby, upon 2 teams in same room, press play to start game

# song names
song_dict = {
    'A': "I Gotta Feeling", 
    'B': 'American Teenager',
    'C': 'Somebody That I Used To Know',
    'D': 'You Belong With Me',
    'E': 'All You Need Is Love',
    'F': 'While My Guitar Gently Weeps'}

class Button:
    def __init__(self, text, x_pos, y_pos, enabled, screen, x_size = 300, y_size=40, toggle = True, song = False, clickable = True):
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
        #self.draw()

    def draw(self):
        # could change size or add it to parameters later
        if not self.enabled:
            return
        font = pygame.font.Font('freesansbold.ttf', 20)
        button_text = font.render(self.text, True, 'black')
        button_rect = pygame.rect.Rect((self.x_pos, self.y_pos), (self.x_size, self.y_size))
        if self.check_hover():
            pygame.draw.rect(self.screen, 'purple', button_rect, 0, 5)
        else:
            pygame.draw.rect(self.screen, 'pink', button_rect, 0 , 5)
        # add outline to button
        pygame.draw.rect(self.screen, 'black', button_rect, 2, 5)
        if self.song:
            self.screen.blit(button_text, (self.x_pos+35, self.y_pos+10))
        else:
            self.screen.blit(button_text, (self.x_pos+(self.x_size/4.5), self.y_pos+(self.y_size/4)))
    
    def draw_toggle(self):
        if not self.enabled:
            return
        font = pygame.font.Font('freesansbold.ttf', 20)
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
    # TODO add flags to trigger condition
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
        pass

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
        #print("parse lobbies: " + msg)
        if msg == "" or msg == "Z":
            return lobbies
        msg = msg[2:]
        lobby_list = msg.split(',')
        #print("lobby list: " + str(lobby_list))
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
        menu_mqtt_client.on_connect = mqtt_lib.menu_mqtt_on_connect
        menu_mqtt_client.on_disconnect = mqtt_lib.menu_mqtt_on_disconnect
        menu_mqtt_client.on_message = mqtt_lib.menu_mqtt_on_message
        menu_mqtt_client.connect_async('mqtt.eclipseprojects.io')
        menu_mqtt_client.loop_start()

        remote_client = mqtt.Client() 
        remote_client.on_connect = mqtt_lib.server_on_connect
        remote_client.on_disconnect = mqtt_lib.server_on_disconnect
        remote_client.on_message = mqtt_lib.server_on_message
        #remote_client.on_publish = mqtt_lib.server_on_publish
        remote_client.connect_async('mqtt.eclipseprojects.io')
        remote_client.loop_start()

        res = (800,600) # screen resolution
        screen = pygame.display.set_mode(res) # opens up a window 
        smallfont = pygame.font.SysFont('Ariel',35) # defining a font 

        menu_screen = True # start on menu screen
        settings_screen = False
        tutorial_screen = False
        song_screen = False
        lobby_screen = False
        waiting_room_screen = False
        open_lobby_screen = False
        song_letter = 'A'

        # define buttons
        start_button = Button('Start!', 250, 220, True, screen)
        settings_button = Button('Settings', 250, 270, True, screen)
        tutorial_button = Button('Tutorial', 250, 320, True, screen)
        quit_button = Button('Quit', 250, 370, True, screen)
        remote_button = Button('Multiplayer', 250, 440, True, screen)

        # remote_button = Button(remote_text, 250, 270, False, screen)
        player_text = ['One Player', 'Two Player']
        player_button = Button(player_text, 250, 320, False, screen)
        back_button = Button('Return', 250, 370, False, screen)

        # team one buttons
        # upon clicking create lobby button, we go to song selection screen
        create_lobby_button = Button('Create Lobby', 250, 320, False, screen)
        # after selecting a song, team 1 is now ready --> button says "waiting for team two to join"
        # until team 2 joins
        # join existing lobby --> 
        team1_status = Button('T1 Ready', 150, 300, False, screen, x_size = 200, y_size = 40, clickable = False)
        team2_status = Button('Waiting for T2...', 500, 300, False, screen, x_size = 200, y_size = 40, clickable = False)

        play_button = Button('Play', 400, 300, False, screen, x_size = 80, y_size = 40)
        # join_open_lobby = Button('Join Open Lobby', 250, 270, False, screen)

        # lobby buttons
        lobby1_button = Button("Lobby A", 150, 120, False, screen, x_size=500, song=True)
        lobby2_button = Button("Lobby B", 150, 170, False, screen, x_size=500, song=True)
        lobby3_button = Button("Lobby C", 150, 220, False, screen, x_size=500, song=True)
        lobby4_button = Button("Lobby D", 150, 270, False, screen, x_size=500, song=True)
        lobby_back_button = Button("                Return", 150, 320, False, screen, x_size = 500)
        
        lobbies = []
        lobbies_buttons = []
        lobbies_buttons.append(lobby1_button)
        lobbies_buttons.append(lobby2_button)
        lobbies_buttons.append(lobby3_button)
        lobbies_buttons.append(lobby4_button)

        # song buttons
        song1_button = Button("A: I Gotta Feeling - Black Eyes Peas", 150, 120, False, screen, x_size=500, song=True)
        song2_button = Button("B: American Teenager - Ethel Cain", 150, 170, False, screen, x_size=500, song=True)
        song3_button = Button("C: Somebody That I Used To Know - Gotye", 150, 220, False, screen, x_size=500, song=True)
        song4_button = Button("D: You Belong With Me - Taylor Swift", 150, 270, False, screen, x_size=500, song=True)
        song5_button = Button("E: All You Need Is Love - The Beatles", 150, 320, False, screen, x_size=500, song = True)
        song6_button = Button("F: While My Guitar Gently Weeps - The Beatles", 150, 370, False, screen, x_size=500, song = True)
        song_back_button = Button("                Return", 150, 420, False, screen, x_size = 500)
        songs = []
        songs.append(song1_button)
        songs.append(song2_button)
        songs.append(song3_button)
        songs.append(song4_button)
        songs.append(song5_button)
        songs.append(song6_button)
        # values to be returned: [mt/st, 1p/2p]
            # also will add song name or smth idk how yet
        multi = False
        player_num = 1

        MESSAGE = pygame.USEREVENT + 1
        MESSAGE_REMOTE = pygame.USEREVENT + 2
        while True: 
            # fills the screen with a color 
            #print("loooop")

            # global flags
            quit_click = mqtt_lib.menu_mqtt.QUIT_CLICK # qc
            return_click = mqtt_lib.menu_mqtt.RETURN_CLICK
            message_received = mqtt_lib.menu_mqtt.MESSAGE_RECEIVED
            mqtt_lobbies_list = mqtt_lib.server_mqtt.MQTT_LOBBIES
            mqtt_team2_ready = mqtt_lib.server_mqtt.MQTT_TEAM2_READY
            mqtt_team1_ready = mqtt_lib.server_mqtt.MQTT_TEAM1_READY
            mqtt_remote_received = mqtt_lib.server_mqtt.MQTT_RECEIVED
            #print("mqtt_lobbies_list: " + mqtt_lobbies_list)

            tutorial = False

            #print("Settings click status: ", settings_click)

            screen.fill((242,152,152)) 

            tbd_text = smallfont.render("TBA...", True, 'black')

            # if tutorial_screen:
            #     screen.blit(tbd_text, (300, 300))

            # if waiting_room_screen:
            #     screen.blit(tbd_text, (300, 300))

            start_button.draw()
            settings_button.draw()
            tutorial_button.draw()
            quit_button.draw()
            remote_button.draw()

            # remote_button.draw_toggle()
            player_button.draw_toggle()
            back_button.draw()
            
            create_lobby_button.draw()
            team1_status.draw()
            team2_status.draw()
            play_button.draw()

            for song in songs:
                song.draw()
            
            song_back_button.draw()

            for lobby in lobbies_buttons:
                lobby.draw()
            
            # for testing:
            multi = True
    
            for ev in pygame.event.get(): 
                
                if ev.type == pygame.QUIT or quit_click: 
                    quit_click = False
                    pygame.quit() 
                    
                #checks if a mouse is clicked or message was received
                if ev.type == pygame.MOUSEBUTTONDOWN or ev.type == MESSAGE:
                    if menu_screen:
                        start_click = mqtt_lib.menu_mqtt.START_CLICK # ga
                        settings_click = mqtt_lib.menu_mqtt.SETTINGS_CLICK # sc
                        tutorial_click = mqtt_lib.menu_mqtt.TUTORIAL_CLICK # tc                        #if the mouse is clicked on the button the game is terminated 
                        if start_button.check_click() or start_click:
                            #TODO send any flags to game here
                            mqtt_lib.menu_mqtt.START_CLICK = False
                            #print("new start click status: ", start_click)
                            song_screen = True
                            start_button.enabled = False
                            settings_button.enabled = False
                            tutorial_button.enabled = False
                            quit_button.enabled = False
                            remote_button.enabled = False
                            for song in songs:
                                song.enabled = True
                            song_back_button.enabled = True
                            break
                            #return [multi, player_num]
                        elif quit_button.check_click() or quit_click:
                            #print("Time to quit!")
                            #print("Multi: ", multi)
                            #print("# players: ", player_num)
                            mqtt_lib.menu_mqtt.QUIT_CLICK = False
                            pygame.quit()
                            exit() 
                        elif tutorial_button.check_click() or tutorial_click:
                            mqtt_lib.menu_mqtt.TUTORIAL_CLICK = False
                            tutorial_screen = True
                            menu_screen = False
                            # toggle buttons
                            start_button.enabled = False
                            settings_button.enabled = False
                            tutorial_button.enabled = False
                            quit_button.enabled = False
                            back_button.enabled = True
                            tutorial = True
                            return [multi, player_num, song1_button.text, tutorial]
                            #break
                        elif settings_button.check_click() or settings_click:
                            mqtt_lib.menu_mqtt.SETTINGS_CLICK = False
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
                            remote_button.enabled = False
                            mqtt_lib.menu_mqtt.MULTI_TEAM_CLICK = False
                            mqtt_lib.menu_mqtt.SINGLE_TEAM_CLICK = False
                            mqtt_lib.menu_mqtt.ONE_PLAYER_CLICK= False
                            mqtt_lib.menu_mqtt.TWO_PLAYER_CLICK= False
                            break
                        elif remote_button.check_click():
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
                            multi = True
                            # KATIE TODO need to ping MQTT here for lobby list
                            remote_client.publish("ECE180/remote", "LLR", qos=1)
                            ("lobbies before: " + str(lobbies))
                            lobbies = self.parse_lobbies(mqtt_lobbies_list)
                            print("lobbies after: " + str(lobbies))
                            # loop through current lobbies
                            # for each lobby, enable a button in lobby list
                                # set that button's text to 
                                # song name + # of players from lobby[0] and lobby[1]
                            i = 0
                            for lobby in lobbies:
                                print(lobby)
                                lobbies_buttons[i].enabled = True
                                player_num = lobby[1]
                                lobby_text = song_dict[lobby[0]] + ", #Players = " + lobby[1]
                                lobbies_buttons[i].text = lobby_text
                                i += 1
                            break
                        
                    if settings_screen:
                        #single_team_click = mqtt_lib.menu_mqtt.SINGLE_TEAM_CLICK # st
                        #multi_team_click = mqtt_lib.menu_mqtt.MULTI_TEAM_CLICK # mt
                        one_player_click = mqtt_lib.menu_mqtt.ONE_PLAYER_CLICK # 1p
                        two_player_click = mqtt_lib.menu_mqtt.TWO_PLAYER_CLICK # 2p
                        if back_button.check_click() or return_click: # TODO ADD FLAG
                            mqtt_lib.menu_mqtt.RETURN_CLICK = False
                            #print("back to da menu")
                            menu_screen = True
                            settings_screen = False
                            # toggle buttons
                            # remote_button.enabled = False
                            player_button.enabled = False
                            back_button.enabled = False
                            start_button.enabled = True
                            settings_button.enabled = True
                            tutorial_button.enabled = True
                            quit_button.enabled = True
                            remote_button.enabled = True
                            break
                        # elif remote_button.check_toggle_click():
                        #     mqtt_lib.menu_mqtt.RETURN_CLICK = False
                        #     remote_button.toggle = not remote_button.toggle
                        #     multi = not multi
                        # elif multi_team_click and not multi:
                        #     multi = True
                        #     remote_button.toggle = not remote_button.toggle
                        #     mqtt_lib.menu_mqtt.MULTI_TEAM_CLICK= False
                        # elif single_team_click and multi:
                        #     multi = False
                        #     remote_button.toggle = not remote_button.toggle
                        #     single_team_click = False
                        #     mqtt_lib.menu_mqtt.SINGLE_TEAM_CLICK= False
                        if player_button.check_toggle_click():
                            player_button.toggle = not player_button.toggle
                            if player_num == 1:
                                player_num = 2
                            elif player_num == 2:
                                player_num = 1
                        elif one_player_click:
                            mqtt_lib.menu_mqtt.ONE_PLAYER_CLICK= False
                            player_button.toggle = not player_button.toggle
                            player_num = 1
                        elif two_player_click:
                            player_button.toggle = not player_button.toggle
                            mqtt_lib.menu_mqtt.TWO_PLAYER_CLICK= False
                            player_num = 2
                    """if tutorial_screen:
                        if back_button.check_click() or return_click: 
                            mqtt_lib.menu_mqtt.RETURN_CLICK = False
                            menu_screen = True
                            tutorial_screen = False
                            # toggle buttons
                            start_button.enabled = True
                            settings_button.enabled = True
                            tutorial_button.enabled = True
                            quit_button.enabled = True
                            back_button.enabled = False
                            tutorial = True
                            return [multi, player_num, tutorial]"""
                    if song_screen:
                        song_a = mqtt_lib.menu_mqtt.SONG_A
                        song_b = mqtt_lib.menu_mqtt.SONG_B
                        song_c = mqtt_lib.menu_mqtt.SONG_C
                        song_d = mqtt_lib.menu_mqtt.SONG_D
                        song_e = mqtt_lib.menu_mqtt.SONG_E
                        song_f = mqtt_lib.menu_mqtt.SONG_F
                        tutorial = False
                        if song_back_button.check_click() or return_click: 
                            if multi:
                                multi = False
                            mqtt_lib.menu_mqtt.RETURN_CLICK = False
                            menu_screen = True
                            song_screen = False
                            # toggle buttons
                            start_button.enabled = True
                            settings_button.enabled = True
                            tutorial_button.enabled = True
                            quit_button.enabled = True
                            for song in songs:
                                song.enabled = False
                            song_back_button.enabled = False
                            break
                        #KATIE TODO add if multiplayer mode, can't go back to menu?
                        elif song1_button.check_click() or song_a:
                            mqtt_lib.menu_mqtt.SONG_A = False
                            return [multi, player_num, song1_button.text, tutorial]
                        elif song2_button.check_click() or song_b:
                            mqtt_lib.menu_mqtt.SONG_B = False
                            return [multi, player_num, song2_button.text, tutorial]
                        elif song3_button.check_click() or song_c:
                            mqtt_lib.menu_mqtt.SONG_C = False
                            return [multi, player_num, song3_button.text, tutorial]
                        elif song4_button.check_click() or song_d:
                            mqtt_lib.menu_mqtt.SONG_D = False
                            return [multi, player_num, song4_button.text, tutorial]
                        elif song5_button.check_click() or song_e:
                            mqtt_lib.menu_mqtt.SONG_E = False
                            return [multi, player_num, song5_button.text, tutorial]
                        elif song6_button.check_click() or song_f:
                            mqtt_lib.menu_mqtt.SONG_F = False
                            return [multi, player_num, song6_button.text, tutorial]
                    if lobby_screen:
                        for lobby_button in lobbies_buttons:
                            if lobby_button.enabled and lobby_button.check_click():
                                waiting_room_screen = True
                                lobby_screen = False
                                #print("lobby button opened!")
                                back_button.text = "Return to main menu"
                                team2_status.text = "T2 Ready"
                                team1_status.enabled = True
                                team2_status.enabled = True
                                lobby_button.enabled = False
                                create_lobby_button.enabled = False
                                remote_client.publish("ECE180/remote", "T2_READY", qos=1)
                                lobbies_buttons[0].text = lobby_button.text
                                lobbies_buttons[0].enabled = True
                                team1 = False
                                break
                        if back_button.check_click():
                            # print("back to da menu")
                            menu_screen = True
                            lobby_screen = False
                            # toggle buttons
                            start_button.enabled = True
                            settings_button.enabled = True
                            tutorial_button.enabled = True
                            quit_button.enabled = True
                            remote_button.enabled = True
                            back_button.enabled = False
                            remote_button.enabled = True
                            team1_status.enabled = True
                            team2_status.enabled = True
                            create_lobby_button.enabled = False
                            for lobby in lobbies_buttons:
                                lobby.enabled = False
                            break
                        if create_lobby_button.check_click():
                            open_lobby_screen = True
                            #song_screen = True
                            #print("clicked create lobby screen")
                            lobby_screen = False
                            back_button.enabled = False
                            quit_button.enabled = False
                            song_back_button.enabled = True
                            create_lobby_button.enabled = False
                            team1 = True
                            for song in songs:
                                song.enabled = True
                            break
                        if mqtt_remote_received:
                            lobbies = self.parse_lobbies(mqtt_lobbies_list)
                            i = 0
                            for lobby in lobbies:
                                lobbies_buttons[i].enabled = True
                                player_num = lobby[1]
                                lobby_text = song_dict[lobby[0]] + ", #Players = " + lobby[1]
                                lobbies_buttons[i].text = lobby_text
                                i += 1
                            break
                    if open_lobby_screen:
                        # KATIE TODO if multi = false, go back to menu (smth is wrong)
                        #print("on open lobby screen")
                        song_a = mqtt_lib.menu_mqtt.SONG_A
                        song_b = mqtt_lib.menu_mqtt.SONG_B
                        song_c = mqtt_lib.menu_mqtt.SONG_C
                        song_d = mqtt_lib.menu_mqtt.SONG_D
                        song_e = mqtt_lib.menu_mqtt.SONG_E
                        song_f = mqtt_lib.menu_mqtt.SONG_F
                        tutorial = False
                        team1 = True
                        if song_back_button.check_click() or return_click: 
                            if multi:
                                multi = False
                            mqtt_lib.menu_mqtt.RETURN_CLICK = False
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
                            break
                        #KATIE TODO 
                        elif song1_button.check_click() or song_a:
                            mqtt_lib.menu_mqtt.SONG_A = False
                            # launch lobby into waiting room
                            waiting_room_screen = True
                            # toggle buttons
                            for song in songs:
                                song.enabled = False
                            song_back_button.enabled = False
                            team1_status.enabled = True
                            team2_status.enabled = True
                            back_button.text = "Return to main menu"
                            back_button.enabled = True
                            lobbies_buttons[0].enabled = True
                            lobby_text = song_dict['A'] + ", #Players = " + str(player_num)
                            lobbies_buttons[0].text = lobby_text
                            lobbies_buttons[0].clickable = False
                            song_text = 'A'
                            # publish to MQTT TODO
                            msg = "A" + str(player_num)
                            remote_client.publish("ECE180/remote", msg, qos=1)
                            break
                            #return [multi, player_num, song1_button.text, tutorial]
                        elif song2_button.check_click() or song_b:
                            mqtt_lib.menu_mqtt.SONG_B = False
                            # launch lobby into waiting room
                            waiting_room_screen = True
                            # toggle buttons
                            for song in songs:
                                song.enabled = False
                            song_back_button.enabled = False
                            team1_status.enabled = True
                            team2_status.enabled = True
                            back_button.text = "Return to main menu"
                            back_button.enabled = True
                            lobbies_buttons[0].enabled = True
                            lobby_text = song_dict['B'] + ", #Players = " + str(player_num)
                            lobbies_buttons[0].text = lobby_text
                            lobbies_buttons[0].clickable = False
                            song_text = 'B'
                            # publish to MQTT TODO
                            msg = "B" + str(player_num)
                            remote_client.publish("ECE180/remote", msg, qos=1)
                            # remote_client.publish("ECE180/remote", "T1_READY", qos=1)
                            break
                            #return [multi, player_num, song2_button.text, tutorial]
                        elif song3_button.check_click() or song_c:
                            mqtt_lib.menu_mqtt.SONG_C = False
                            # launch lobby into waiting room
                            waiting_room_screen = True
                            # toggle buttons
                            for song in songs:
                                song.enabled = False
                            song_back_button.enabled = False
                            team1_status.enabled = True
                            team2_status.enabled = True
                            back_button.text = "Return to main menu"
                            back_button.enabled = True
                            lobbies_buttons[0].enabled = True
                            song_text = 'C'
                            lobby_text = song_dict['C'] + ", #Players = " + str(player_num)
                            lobbies_buttons[0].text = lobby_text
                            lobbies_buttons[0].clickable = False
                            # publish to MQTT TODO
                            msg = "C" + str(player_num)
                            remote_client.publish("ECE180/remote", msg, qos=1)
                            # remote_client.publish("ECE180/remote", "T1_READY", qos=1)
                            break
                            #return [multi, player_num, song3_button.text, tutorial]
                        elif song4_button.check_click() or song_d:
                            mqtt_lib.menu_mqtt.SONG_D = False
                            # launch lobby into waiting room
                            waiting_room_screen = True
                            # toggle buttons
                            for song in songs:
                                song.enabled = False
                            song_back_button.enabled = False
                            team1_status.enabled = True
                            team2_status.enabled = True
                            back_button.text = "Return to main menu"
                            back_button.enabled = True
                            lobbies_buttons[0].enabled = True
                            lobby_text = song_dict['D'] + ", #Players = " + str(player_num)
                            lobbies_buttons[0].text = lobby_text
                            lobbies_buttons[0].clickable = False
                            song_text = 'D'
                            # publish to MQTT TODO
                            msg = "D" + str(player_num)
                            remote_client.publish("ECE180/remote", msg, qos=1)
                            # remote_client.publish("ECE180/remote", "T1_READY", qos=1)
                            break
                            #return [multi, player_num, song4_button.text, tutorial]
                        elif song5_button.check_click() or song_e:
                            mqtt_lib.menu_mqtt.SONG_E = False
                            # launch lobby into waiting room
                            waiting_room_screen = True
                            # toggle buttons
                            for song in songs:
                                song.enabled = False
                            song_back_button.enabled = False
                            team1_status.enabled = True
                            team2_status.enabled = True
                            back_button.text = "Return to main menu"
                            back_button.enabled = True
                            lobbies_buttons[0].enabled = True
                            lobby_text = song_dict['E'] + ", #Players = " + str(player_num)
                            lobbies_buttons[0].text = lobby_text
                            lobbies_buttons[0].clickable = False
                            song_text = 'E'
                            # publish to MQTT TODO
                            msg = "E" + str(player_num)
                            remote_client.publish("ECE180/remote", msg, qos=1)
                            # remote_client.publish("ECE180/remote", "T1_READY", qos=1)
                            break
                            #return [multi, player_num, song5_button.text, tutorial]
                        elif song6_button.check_click() or song_f:
                            mqtt_lib.menu_mqtt.SONG_F = False
                            # launch lobby into waiting room
                            waiting_room_screen = True
                            # toggle buttons
                            for song in songs:
                                song.enabled = False
                            song_back_button.enabled = False
                            team1_status.enabled = True
                            team2_status.enabled = True
                            back_button.text = "Return to main menu"
                            back_button.enabled = True
                            lobbies_buttons[0].enabled = True
                            lobby_text = song_dict['F'] + ", #Players = " + str(player_num)
                            lobbies_buttons[0].text = lobby_text
                            lobbies_buttons[0].clickable = False
                            song_text = 'F'
                            # publish to MQTT TODO
                            msg = "F" + str(player_num)
                            remote_client.publish("ECE180/remote", msg, qos=1)
                            # remote_client.publish("ECE180/remote", "T1_READY", qos=1)
                            break
                            #return [multi, player_num, song6_button.text, tutorial]
                    if waiting_room_screen:
                        # if team 1:
                        #if team1:
                        if team1 and play_button.check_click():
                            print("team 1 launching")
                            remote_client.publish("ECE180/remote", "T1_READY", qos=1)
                            return [multi, player_num, song_text, tutorial, team1]
                        elif team1 and mqtt_team2_ready:
                            #print("yuh yuh yuh")
                            team2_status.text = "T2 Ready"
                            play_button.enabled = True
                            break
                        # draw "waiting for team 2 to join" on play button
                            # when team 2 joins change to play button
                        #print("mqtt team 1 status: " + str(mqtt_team1_ready))
                        #print("mqtt team 2 status: " + str(mqtt_team2_ready))
                        # if team 2: 
                        if not team1 and mqtt_team1_ready:
                        # draw "waiting for both teams to press start"
                            print("team 2 launching")
                            return [multi, player_num, song_text, tutorial, team1]
                            # draw play button
                        if back_button.check_click():
                            menu_screen = True
                            back_button.text = "Return"
                            menu_screen = True
                            waiting_room_screen = False
                            # toggle buttons
                            back_button.enabled = False
                            team1_status.enabled = False
                            team2_status.enabled = False
                            remote_button.enabled = True
                            start_button.enabled = True
                            settings_button.enabled = True
                            tutorial_button.enabled = True
                            quit_button.enabled = True
                            lobbies_buttons[0].enabled = False
                            break
                                                    
            if message_received:
                pygame.event.post(pygame.event.Event(MESSAGE))
                message_received = False
            if mqtt_remote_received:
                pygame.event.post(pygame.event.Event(MESSAGE))
                mqtt_remote_received = False
            # updates the frames of the game 
            pygame.display.update() 

