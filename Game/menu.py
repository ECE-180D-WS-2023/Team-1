
import time
import keyboard
import pygame
import pygame_menu

pygame.init()

# create game window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Main Menu")

x, y = screen.get_size()

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
mymenu.add.button('Start game!', Gameplay)
mymenu.add.button('Tutorial', Tutorial)
mymenu.add.button('Settings', Settings)
mymenu.add.button('Quit', pygame_menu.events.EXIT)


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
