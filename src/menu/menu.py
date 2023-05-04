import time
import keyboard
import pygame
import paho.mqtt.client as mqtt
from menu import mqtt_lib



# TODO HELP ???
#from menu import menu_mqtt

#TODO (spring quarter)
# goal: menu integrated with voice controls and gameplay
# upon "start game," should go to song selection screen
    # for now, should just launch the game - done
    # need to send information from menu to game --> returns an array of booleans for multi/single and 1p/2p
        # idk what im gonna do for song selection yet
# upon "tutorial," should go to tutorial mode (not implemented yet) - done
# upon "settings," go to settings page and choose one team vs multi team, 1p vs 2p - done


# TODO 4/20/2023: 
# Make mqtt file w/ the onmessage, disconnect, connect (look at imu_mqtt.py) - done
    # i gotta tell andrew the codes so he can write the messages 

class Button:
    def __init__(self, text, x_pos, y_pos, enabled, screen, x_size = 300, y_size=40, toggle = True, song = False):
        self.text = text
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.enabled = enabled
        self.screen = screen
        self.x_size = x_size
        self.y_size= y_size
        self.toggle = toggle
        self.song = song
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
            self.screen.blit(button_text, (self.x_pos+100, self.y_pos+10))
    
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
    
    def start(self):
        # initializing the constructor 
        pygame.init()

        #initializing mqtt client for voice recognition
        menu_mqtt_client = mqtt.Client()
        menu_mqtt_client.on_connect = mqtt_lib.menu_mqtt_on_connect
        menu_mqtt_client.on_disconnect = mqtt_lib.menu_mqtt_on_disconnect
        menu_mqtt_client.on_message = mqtt_lib.menu_mqtt_on_message
        menu_mqtt_client.connect_async('mqtt.eclipseprojects.io')
        menu_mqtt_client.loop_start()

        res = (800,600) # screen resolution
        screen = pygame.display.set_mode(res) # opens up a window 
        smallfont = pygame.font.SysFont('Ariel',35) # defining a font 

        menu_screen = True # start on menu screen
        settings_screen = False
        tutorial_screen = False
        song_screen = False

        # define buttons
        start_button = Button('Start!', 250, 220, True, screen)
        settings_button = Button('Settings', 250, 270, True, screen)
        tutorial_button = Button('Tutorial', 250, 320, True, screen)
        quit_button = Button('Quit', 250, 370, True, screen)

        remote_text = ['Single Team', 'Multi Team']
        remote_button = Button(remote_text, 250, 270, False, screen)
        player_text = ['One Player', 'Two Player']
        player_button = Button(player_text, 250, 320, False, screen)
        back_button = Button('Return', 250, 370, False, screen)

        # song buttons
        song1_button = Button("A: I Gotta Feeling - Black Eyes Peas", 150, 120, False, screen, x_size=500, song=True)
        song2_button = Button("B: American Teenager - Ethel Cain", 150, 170, False, screen, x_size=500, song=True)
        song3_button = Button("C: Somebody That I Used To Know - Gotye", 150, 220, False, screen, x_size=500, song=True)
        song4_button = Button("D: You Belong With Me - Taylor Swift", 150, 270, False, screen, x_size=500, song=True)
        song5_button = Button("E: All You Need Is Love - The Beatles", 150, 320, False, screen, x_size=500, song = True)
        song6_button = Button("F: While My Guitar Gently Weeps - The Beatles", 150, 370, False, screen, x_size=500, song = True)
        song_back_button = Button("                Return", 150, 420, False, screen, x_size = 500)

        # values to be returned: [mt/st, 1p/2p]
            # also will add song name or smth idk how yet
        multi = False
        player_num = 1

        MESSAGE = pygame.USEREVENT + 1
        while True: 
            # fills the screen with a color 
            #print("loooop")

            # global flags
            start_click = mqtt_lib.menu_mqtt.START_CLICK # ga
            settings_click = mqtt_lib.menu_mqtt.SETTINGS_CLICK # sc
            tutorial_click = mqtt_lib.menu_mqtt.TUTORIAL_CLICK # tc
            quit_click = mqtt_lib.menu_mqtt.QUIT_CLICK # qc
            single_team_click = mqtt_lib.menu_mqtt.SINGLE_TEAM_CLICK # st
            multi_team_click = mqtt_lib.menu_mqtt.MULTI_TEAM_CLICK # mt
            one_player_click = mqtt_lib.menu_mqtt.ONE_PLAYER_CLICK # 1p
            two_player_click = mqtt_lib.menu_mqtt.TWO_PLAYER_CLICK # 2p
            return_click = mqtt_lib.menu_mqtt.RETURN_CLICK
            message_received = mqtt_lib.menu_mqtt.MESSAGE_RECEIVED
            song_a = mqtt_lib.menu_mqtt.SONG_A
            song_b = mqtt_lib.menu_mqtt.SONG_B
            song_c = mqtt_lib.menu_mqtt.SONG_C
            song_d = mqtt_lib.menu_mqtt.SONG_D
            song_e = mqtt_lib.menu_mqtt.SONG_E
            song_f = mqtt_lib.menu_mqtt.SONG_F

            print("Settings click status: ", settings_click)

            screen.fill((242,152,152)) 

            tbd_text = smallfont.render("TBA...", True, 'black')

            if tutorial_screen:
                screen.blit(tbd_text, (300, 300))

            #TODO add tutorial screen
            start_button.draw()
            settings_button.draw()
            tutorial_button.draw()
            quit_button.draw()

            remote_button.draw_toggle()
            player_button.draw_toggle()
            back_button.draw()

            song1_button.draw()
            song2_button.draw()
            song3_button.draw()
            song4_button.draw()
            song5_button.draw()
            song6_button.draw()
            song_back_button.draw()
            
            for ev in pygame.event.get(): 
                
                if ev.type == pygame.QUIT or quit_click: 
                    quit_click = False
                    pygame.quit() 
                    
                #checks if a mouse is clicked or message was received
                if ev.type == pygame.MOUSEBUTTONDOWN or ev.type == MESSAGE:
                    if menu_screen:
                        #if the mouse is clicked on the button the game is terminated 
                        if start_button.check_click() or start_click:
                            #TODO send any flags to game here
                            mqtt_lib.menu_mqtt.START_CLICK = False
                            #print("new start click status: ", start_click)
                            song_screen = True
                            start_button.enabled = False
                            settings_button.enabled = False
                            tutorial_button.enabled = False
                            quit_button.enabled = False
                            song1_button.enabled = True
                            song2_button.enabled = True
                            song3_button.enabled = True
                            song4_button.enabled = True
                            song5_button.enabled = True
                            song6_button.enabled = True
                            song_back_button.enabled = True
                            break
                            #return [multi, player_num]
                        elif quit_button.check_click() or quit_click:
                            print("Time to quit!")
                            print("Multi: ", multi)
                            print("# players: ", player_num)
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
                            break
                        elif settings_button.check_click() or settings_click:
                            mqtt_lib.menu_mqtt.SETTINGS_CLICK = False
                            settings_screen = True
                            menu_screen = False
                            # toggle buttons
                            start_button.enabled = False
                            settings_button.enabled = False
                            tutorial_button.enabled = False
                            quit_button.enabled = False
                            remote_button.enabled = True
                            player_button.enabled = True
                            back_button.enabled = True
                            mqtt_lib.menu_mqtt.MULTI_TEAM_CLICK = False
                            mqtt_lib.menu_mqtt.SINGLE_TEAM_CLICK = False
                            mqtt_lib.menu_mqtt.ONE_PLAYER_CLICK= False
                            mqtt_lib.menu_mqtt.TWO_PLAYER_CLICK= False
                            break
                    if settings_screen:
                        if back_button.check_click() or return_click: # TODO ADD FLAG
                            mqtt_lib.menu_mqtt.RETURN_CLICK = False
                            print("back to da menu")
                            menu_screen = True
                            settings_screen = False
                            # toggle buttons
                            remote_button.enabled = False
                            player_button.enabled = False
                            back_button.enabled = False
                            start_button.enabled = True
                            settings_button.enabled = True
                            tutorial_button.enabled = True
                            quit_button.enabled = True
                            break
                        elif remote_button.check_toggle_click():
                            mqtt_lib.menu_mqtt.RETURN_CLICK = False
                            remote_button.toggle = not remote_button.toggle
                            multi = not multi
                        elif multi_team_click and not multi:
                            multi = True
                            remote_button.toggle = not remote_button.toggle
                            mqtt_lib.menu_mqtt.MULTI_TEAM_CLICK= False
                        elif single_team_click and multi:
                            multi = False
                            remote_button.toggle = not remote_button.toggle
                            single_team_click = False
                            mqtt_lib.menu_mqtt.SINGLE_TEAM_CLICK= False
                        elif player_button.check_toggle_click():
                            player_button.toggle = not player_button.toggle
                            if player_num == 1:
                                player_num = 2
                            elif player_num == 2:
                                player_num = 1
                        elif one_player_click and player_num == 2:
                            mqtt_lib.menu_mqtt.ONE_PLAYER_CLICK= False
                            player_button.toggle = not player_button.toggle
                            player_num = 1
                        elif two_player_click and player_num == 1:
                            player_button.toggle = not player_button.toggle
                            mqtt_lib.menu_mqtt.TWO_PLAYER_CLICK= False
                            player_num = 2
                    if tutorial_screen:
                        if back_button.check_click() or return_click: # TODO ADD FLAG
                            mqtt_lib.menu_mqtt.RETURN_CLICK = False
                            menu_screen = True
                            tutorial_screen = False
                            # toggle buttons
                            start_button.enabled = True
                            settings_button.enabled = True
                            tutorial_button.enabled = True
                            quit_button.enabled = True
                            back_button.enabled = False
                            break
                    if song_screen:
                        if song_back_button.check_click() or return_click: # TODO ADD FLAG
                            mqtt_lib.menu_mqtt.RETURN_CLICK = False
                            menu_screen = True
                            song_screen = False
                            # toggle buttons
                            start_button.enabled = True
                            settings_button.enabled = True
                            tutorial_button.enabled = True
                            quit_button.enabled = True
                            song1_button.enabled = False
                            song2_button.enabled = False
                            song3_button.enabled = False
                            song4_button.enabled = False
                            song5_button.enabled = False
                            song6_button.enabled = False
                            song_back_button.enabled = False
                            break
                        elif song1_button.check_click() or song_a:
                            mqtt_lib.menu_mqtt.SONG_A = False
                            return [multi, player_num, song1_button.text]
                        elif song2_button.check_click() or song_b:
                            mqtt_lib.menu_mqtt.SONG_B = False
                            return [multi, player_num, song2_button.text]
                        elif song3_button.check_click() or song_c:
                            mqtt_lib.menu_mqtt.SONG_C = False
                            return [multi, player_num, song3_button.text]
                        elif song4_button.check_click() or song_d:
                            mqtt_lib.menu_mqtt.SONG_D = False
                            return [multi, player_num, song4_button.text]
                        elif song5_button.check_click() or song_e:
                            mqtt_lib.menu_mqtt.SONG_E = False
                            return [multi, player_num, song5_button.text]
                        elif song6_button.check_click() or song_f:
                            mqtt_lib.menu_mqtt.SONG_F = False
                            return [multi, player_num, song6_button.text]
            if message_received:
                pygame.event.post(pygame.event.Event(MESSAGE))
                message_received = False
            # updates the frames of the game 
            pygame.display.update() 

