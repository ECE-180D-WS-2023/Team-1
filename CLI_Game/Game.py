from Button import Button
from Settings import ROWS, COLS, KEYS
import random
import pygame

DELAY_AFTER_CLICK = 800 # ms
# should contain all the game logic that has internal grid and then eventually
# in main.py updates the print grid... or maybe combine... hmm

# TODO: also probably print some line that indicates where you have to click the button maybe <--- arrow to the
# right of the correct line

# TODO: make it so that buttons dont spawn every round and maybe its like random # --> spawn but
# the spawn chance is like a function of game difficulty
# maybe make game difficulty a setting or BASED ON SONG BPM

# TODO LOW PRIO: make sure that if i spawn multiple buttons, the buttons don't appear in the same row

class Game:
    difficulty = None
    
    # existing buttons in the game
    existing_buttons = []

    score = 0
    
    def __init__(self, difficulty=3):
        self.difficulty = difficulty

    # corresponds to one game cycle
    def update(self):
        # move all of the existing buttons down one row
        for button in self.existing_buttons:
            button.set_row(button.get_row() + 1)
            
        # if the button exceeds the max row / col, then remove from existing button list
        for button in self.existing_buttons:
            if (button.get_row() >= ROWS):
                self.score -= 1
                print("Missed button!")
                pygame.time.wait(DELAY_AFTER_CLICK)
        self.existing_buttons = [button for button in self.existing_buttons if not (button.get_row() >= ROWS)]
        
        # then spawn buttons
        self.__button_spawner()

    # helper function that calculates whether to spawns buttons
    def __button_spawner(self):
        # spawn button if there is less buttons than difficutly, for now spawn 1 button call
        if (len(self.existing_buttons) < self.difficulty):
            # spawn button in random column in the 0th row with random lowercase letter key
            self.__spawn_button(row=0, col=random.randint(0,COLS-1), key=(random.choice(KEYS)))

    # helper function to steadily spawn buttons
    def __spawn_button(self, row, col, key):
        b = Button(row=row, col=col, key=key)
        self.existing_buttons.append(b)

    # for getting button locations in main
    def get_buttons(self):
        return self.existing_buttons

    # helper for key_pressed
    def __button_in_row(self, row):
        for button in self.get_buttons():
            if button.get_row() == row:
                return button

    # get button in the lowest row
    def __button_in_lowest_row(self):
        lowest_row = -1
        lowest_row_button = None
        for button in self.get_buttons():
            if (button.get_row() > lowest_row):
                lowest_row_button = button
                lowest_row = button.get_row()
        return lowest_row_button


    # when key gets pressed, update the game
    # returns True/False, col, row
    # col and row represent place of clicked button
    # true or false represents which button pressed
    # will return -1, -1, -1 if valid key pressed but no button in last 2 rows
    def key_pressed(self, key):
        if key in KEYS:
            button_row = -1
            button_col = -1
            correct = None

            button_in_last_row = self.__button_in_row(ROWS-1)
            button_in_2ndlast_row = self.__button_in_row(ROWS-2)

            # see if key is in last 2 rows, if it is then record location of button and erase
            if (button_in_last_row):
                button_row = button_in_last_row.get_row()
                button_col = button_in_last_row.get_col()
                self.existing_buttons.remove(button_in_last_row)
                
                if button_in_last_row.get_key() == key:
                    correct = True
                else:
                    correct = False
            elif (button_in_2ndlast_row):
                button_row = button_in_2ndlast_row.get_row()
                button_col = button_in_2ndlast_row.get_col()
                self.existing_buttons.remove(button_in_2ndlast_row)
                
                if button_in_2ndlast_row.get_key() == key:
                    correct = True
                else:
                    correct = False
            else: 
                # valid key pressed but no button in last two rows
                lowest_button = self.__button_in_lowest_row()
                button_row = lowest_button.get_row()
                button_col = lowest_button.get_col()
                self.existing_buttons.remove(lowest_button)
                correct = -1
        else:
            lowest_button = self.__button_in_lowest_row()
            button_row = lowest_button.get_row()
            button_col = lowest_button.get_col()
            self.existing_buttons.remove(lowest_button)
            correct = -1
        return correct, button_row, button_col
