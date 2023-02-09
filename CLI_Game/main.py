from Grid import Grid
from Game import Game
import time

DELAY_PER_FRAME = 0.7 # s

# initialize board
my_grid = Grid()
my_game = Game()

# first cycle just print empty grid
my_grid.print_grid()
time.sleep(DELAY_PER_FRAME)

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
    
    time.sleep(DELAY_PER_FRAME)
