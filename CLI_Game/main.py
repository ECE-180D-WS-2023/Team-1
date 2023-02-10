from Grid import Grid
from Game import Game
import pygame

DELAY_PER_FRAME = 700 # ms

# quitting flag
quit = False

# initialize board
my_grid = Grid()
my_game = Game()

# first cycle just print empty grid
my_grid.print_grid()
# need init to use pygame
pygame.init()
WIDTH=600
HEIGHT=480
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))

# keep track of score
score = 0

# function that evaluates button press and then updates the grid
# prints grind how it is currently but just with quick replace on the pressed row/col
def evaluate_press(correct, row, col, grid):
    global score

    if correct == -1:
        print("no button in last two rows")
    elif correct == True:
        grid.set_point(row, col, '*')
        score += 1
    elif correct == False:
        grid.set_point(row, col, '-')

    grid.print_grid()
    print("Score: ", score)
    if correct == False:
        print("Wrong Key Pressed!")

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