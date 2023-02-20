from Grid import Grid
from Game import Game
import pygame

# also do a score check in Game -- 
# because need to quick print grid 
# and also need to print score 
# if score >> some value then move difficulty up

# so Game needs info about score for difficulty
# and main needs info about clicks for updating grid
# actually main shouldn't need to do quick prints
    # just get game to do quick print by passing grid into game method
    # main doesn't even need score... if i really want main
    # to have score just do a game.get_score

DELAY_PER_FRAME = 700 # ms
DELAY_AFTER_CLICK = 800 # ms

# quitting flag
quit = False

# initialize board
my_grid = Grid()
my_game = Game()

# first cycle just print empty grid
my_grid.print_grid()
# need init to use pygame
pygame.init()
WIDTH=100
HEIGHT=100
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))

# keep track of score
score = 0

# function that evaluates button press and then updates the grid
# prints grind how it is currently but just with quick replace on the pressed row/col
def evaluate_press(correct, row, col, grid):
    global score

    if correct == -1 or correct == False:
        grid.set_point(row, col, '-')
        score -= 1
    elif correct == True:
        grid.set_point(row, col, '*')
        score += 1

    grid.print_grid()
    print("Score: ", score)
    if correct == False:
        print("Wrong Key Pressed!")
    elif correct == -1:
        print("Wrong Key Pressed!")
    elif correct == True:
        print("Nice!")
    
    pygame.time.wait(DELAY_AFTER_CLICK)

# keep printing grid every DELAY_PER_FRAME s for now
while (True):
    # update game
    my_game.update()

    # reset grid to all . and then update new button location
    my_grid.reset_grid()
    # update grid based on where buttons currently are
    for button in my_game.get_buttons():
        button_row, button_col = button.get_location()
        button_key = button.get_key()
        my_grid.set_point(button_row, button_col, button_key)

    # print grid
    my_grid.print_grid()
    print("Score: ", score)

    # wait certain amount of time before updating screen
    last_time = pygame.time.get_ticks()
    # keypress registering
    correct = None
    row = None
    col = None
    # until new frame time, keep checking for button press
    while(pygame.time.get_ticks() - last_time < DELAY_PER_FRAME):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    quit = True
                else:
                    # run function to get which key is pressed
                    correct, row, col = my_game.key_pressed(pygame.key.name(event.key))
                    # then perform print operation
                    evaluate_press(correct, row, col, my_grid)
                    

    if (quit):
        break