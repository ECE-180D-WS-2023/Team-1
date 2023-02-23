
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

# menu
go = True

# main menu
mymenu = pygame_menu.Menu("Human Guitar Hero!", x, y, theme=pygame_menu.themes.THEME_BLUE)
mymenu.add.button('Start game!')
mymenu.add.button('Settings')
mymenu.add.button('Quit', pygame_menu.events.EXIT)

# settings
settings = pygame_menu.Menu("Settings", x, y, theme=pygame_menu.themes.THEME_BLUE)
settings.add.button('Calibration')
settings.add.button("Mode")

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

#menu outline:
#TODO generate menu with scrolling options (?), be able to select one of them
#TODO maybe print out song name and then they can press left or right arrows to scroll
#TODO print selected song + tempo of selected song

#tempo outline:
#TODO get tempo from song files and add to bank
#TODO audio processing heavy :(


song_bank = {
    "Antihero": 220,
    "American Teenager": 180,
    "Firework": 200,
    "Joanne": 140,
    "Cruel Summer": 170
}

#important: needs to be run as root user
#TODO change to pygame instead
#note for right now: pygame opens a window that will be blank, click on the window then type input
#output will still be cli on terminal
def generate_menu():
    print("Use the arrow keys to browse songs and press enter to select a song!\n")
    i = 0
    while(True):
        songs = list(song_bank)
        #user_move = input(songs[i])
        print(songs[i])
        event = keyboard.read_event()
        #if user_move == "a" and i > 0 :
        if event.event_type == keyboard.KEY_DOWN and event.name == 'left' and i > 0:
            i -= 1
        #elif user_move == "d" and i < len(songs)-1:
        elif event.event_type == keyboard.KEY_DOWN and event.name == 'right' and i < len(songs) - 1:
            i += 1
        #elif user_move == "s":
        elif event.event_type == keyboard.KEY_DOWN and event.name == 'enter':
            print("Song selected: {}".format(songs[i]))
            return song_bank[songs[i]]
        elif event.event_type == keyboard.KEY_DOWN and event.name == 'enter' == "q":
            print("Quitting game!")
            break

song = generate_menu()
print(song)