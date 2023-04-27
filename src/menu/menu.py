import time
import keyboard
import pygame
import pygame_menu
import pygame_menu.controls
from pygame_menu.controls import Controller

from pygame.locals import (
    K_q,
    K_1,
    KEYDOWN,
    QUIT,
)

#TODO (spring quarter)
# goal: menu integrated with voice controls and gameplay
# upon "start game," should go to song selection screen
    # for now, should just launch the game
# upon "tutorial," should go to tutorial mode (not implemented yet)
# upon "settings," go to settings page and choose remote vs normal mode


# TODO 4/20/2023: 
# Make mqtt file w/ the onmessage, disconnect, connect (look at imu_mqtt.py)
# import from file, make mqtt client then set the onconnect functions (etc) to the function from file
# parse in 

class Button:
    def __init__(self, text, x_pos, y_pos, enabled, screen, x_size = 300, y_size=40, toggle = True):
        self.text = text
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.enabled = enabled
        self.screen = screen
        self.x_size = 300
        self.y_size=40
        self.toggle = toggle
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
        else: # TODO could add color to parameters
            pygame.draw.rect(self.screen, 'pink', button_rect, 0 , 5)
        # add outline to button
        pygame.draw.rect(self.screen, 'black', button_rect, 2, 5)
        self.screen.blit(button_text, (self.x_pos+100, self.y_pos+10))
    
    def draw_toggle(self):
        if not self.enabled:
            return
        font = pygame.font.Font('freesansbold.ttf', 20)
        option0_text = font.render(self.text[0], True, 'black')
        option1_text = font.render(self.text[1], True, 'black')
        option0_rect = pygame.rect.Rect((self.x_pos, self.y_pos), (145, 40))
        option1_rect = pygame.rect.Rect((self.x_pos + 150, self.y_pos), (145, 40))
        
        """if self.check_hover():
            pygame.draw.rect(self.screen, 'purple', button_rect, 0, 5)
        else: 
            pygame.draw.rect(self.screen, 'pink', button_rect, 0 , 5)"""
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
        button_rect = pygame.rect.Rect((self.x_pos, self.y_pos), (300, 40))
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
        res = (800,600) # screen resolution
        screen = pygame.display.set_mode(res) # opens up a window 
        width = screen.get_width() # stores the width of the screen into a variable 
        height = screen.get_height() # stores the height of the screen into a variable 
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
        
        while True: 
            # fills the screen with a color 
            #print("loooop")
            screen.fill((242,152,152)) 

            tbd_text = smallfont.render("TBA...", True, 'black')

            if tutorial_screen:
                screen.blit(tbd_text, (300, 300))
            
            if song_screen:
                screen.blit(tbd_text, (300, 300))

            #TODO add tutorial screen
            start_button.draw()
            settings_button.draw()
            tutorial_button.draw()
            quit_button.draw()

            remote_button.draw_toggle()
            player_button.draw_toggle()
            back_button.draw()
            
            for ev in pygame.event.get(): 
                
                if ev.type == pygame.QUIT: 
                    pygame.quit() 
                    
                #checks if a mouse is clicked 
                if ev.type == pygame.MOUSEBUTTONDOWN: 
                    if menu_screen:
                        #if the mouse is clicked on the button the game is terminated 
                        if start_button.check_click():
                            #TODO send any flags to game here
                            print("Start game!")
                            song_screen = True
                            start_button.enabled = False
                            settings_button.enabled = False
                            tutorial_button.enabled = False
                            quit_button.enabled = False
                            back_button.enabled = True
                        if quit_button.check_click():
                            print("Time to quit!")
                            pygame.quit()
                            exit() 
                        if tutorial_button.check_click():
                            tutorial_screen = True
                            menu_screen = False
                            # toggle buttons
                            start_button.enabled = False
                            settings_button.enabled = False
                            tutorial_button.enabled = False
                            quit_button.enabled = False
                            back_button.enabled = True
                            break
                        if settings_button.check_click():
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
                            break
                    if settings_screen:
                        if remote_button.check_toggle_click():
                            remote_button.toggle = not remote_button.toggle
                        if player_button.check_toggle_click():
                            player_button.toggle = not player_button.toggle
                        if back_button.check_click():
                            menu_screen = True
                            settings_screen = False
                            # toggle buttons
                            start_button.enabled = True
                            settings_button.enabled = True
                            tutorial_button.enabled = True
                            quit_button.enabled = True
                            remote_button.enabled = False
                            player_button.enabled = False
                            back_button.enabled = False
                            break
                    if tutorial_screen:
                        if back_button.check_click():
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
                        if back_button.check_click():
                            menu_screen = True
                            song_screen = False
                            # toggle buttons
                            start_button.enabled = True
                            settings_button.enabled = True
                            tutorial_button.enabled = True
                            quit_button.enabled = True
                            back_button.enabled = False
                            break

            # updates the frames of the game 
            pygame.display.update() 








        # old code
        """pygame.init()
        # create game window
        SCREEN_WIDTH = 800
        SCREEN_HEIGHT = 600

        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Main Menu")

        x, y = screen.get_size()
        # settings
        Settings = pygame_menu.Menu("Settings", x, y, theme=pygame_menu.themes.THEME_BLUE)
        Settings.add.button('Calibration')
        mode_button = Settings.add.dropselect(
            title='Mode?',
            items=[('One team', 0),
                ('Remote multiplayer', 1)],
            font_size=24,
            selection_option_font_size=24
        )

        # game display window placeholder
        Gameplay = pygame_menu.Menu("Gameplay", x, y, theme=pygame_menu.themes.THEME_BLUE)

        # tutorial display window placeholder
        Tutorial = pygame_menu.Menu("Tutorial", x, y, theme=pygame_menu.themes.THEME_BLUE)

        # song menu display window
        Songs = pygame_menu.Menu("Song Selection", x, y, theme=pygame_menu.themes.THEME_BLUE)

        # menu
        go = True

        # button flags
        START_FLAG = False

        # other flags
        SPEECH_FLAG = False

        start_controller = Controller()
        start_controller.apply = self.button_apply(flag=START_FLAG)

        # main menu
        mymenu = pygame_menu.Menu("Human Guitar Hero!", x, y, theme=pygame_menu.themes.THEME_BLUE)
        start = mymenu.add.button('Start game!', Gameplay)
        start.set_controller(start_controller)
        tutorial = mymenu.add.button('Tutorial', Tutorial)
        settings = mymenu.add.button('Settings', Settings)
        quitb = mymenu.add.button('Quit', pygame_menu.events.EXIT)


        while go:
            self.draw_background(screen)

            events = pygame.event.get()
            
            if mymenu.is_enabled():
                mymenu.update(events)
                mymenu.draw(screen)

            for event in events:
                if event.type == KEYDOWN:
                    if event.key == K_q:
                        go = False
                    elif event.key == K_s:
                        START_FLAG = True
                
            
            pygame.display.update()

        pygame.quit()"""



# old code for button
"""# stores the (x,y) coordinates into 
# the variable as a tuple 
mouse = pygame.mouse.get_pos() 

# if mouse is hovered on a button it 
# changes to lighter shade 
if width/2 <= mouse[0] <= width/2+140 and height/2 <= mouse[1] <= height/2+40: 
    pygame.draw.rect(screen,blue_light,[width/2-30,height/2,200,40]) 
    
else: 
    pygame.draw.rect(screen,blue_dark,[width/2-30,height/2,200,40]) 


# superimposing the text onto our button 
screen.blit(start_text , (width/2+50,height/2)) """