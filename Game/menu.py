
import time
import keyboard
import pygame
import pygame_menu
import pygame_menu.controls
from pygame_menu.controls import Controller

pygame.init()

# create game window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Main Menu")

x, y = screen.get_size()

# create custom controller class for interface with voice commands
cust_controller = Controller()

def start_apply(event, menu_object):
    applied = event.key in (pygame.K_a)
    return applied

cust_controller.apply = start_apply

def draw_text (text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_background():
    screen.fill((255, 255, 255))

# song selection
Songmenu = pygame_menu.Menu("Song Selection", x, y, theme=pygame_menu.themes.THEME_BLUE)

# settings
Settings = pygame_menu.Menu("Settings", x, y, theme=pygame_menu.themes.THEME_BLUE)
Settings.add.button('Calibration')
mode_button = Settings.add.dropselect(
    title='Mode?',
    items=[('One team', 0),
           ('Multiplayer', 1)],
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

# main menu
mymenu = pygame_menu.Menu("Human Guitar Hero!", x, y, theme=pygame_menu.themes.THEME_BLUE)
start = mymenu.add.button('Start game!', Gameplay)
start.set_controller(cust_controller)
tutorial = mymenu.add.button('Tutorial', Tutorial)
settings = mymenu.add.button('Settings', Settings)
quitb = mymenu.add.button('Quit', pygame_menu.events.EXIT)


while go:
    draw_background()

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            exit()
    
    if mymenu.is_enabled():
        mymenu.update(events)
        mymenu.draw(screen)
    
    pygame.display.update()

pygame.quit()
