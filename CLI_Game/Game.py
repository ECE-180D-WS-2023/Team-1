from Button import Button
from Settings import ROWS, COLS
import random
import string

# should contain all the game logic that has internal grid and then eventually
# in main.py updates the print grid... or maybe combine... hmm

# TODO: DECREMENT SCORE WHEN LETTER GOES OUT OF SCREEN since this means missed
# PRINT SOME SAD MESSAGE LIKE LETTER MISSED
# TODO: IF BUTTON PRESSED, REGISTER AND CLEAR THAT THING FROM GAME IF THERE EXISTS BUTTON AT LOWEST LEVEL 
# INCREMENT SCORE PRINT ABOVE OR BELOW BOARD GOOD MESSAGE
# TODO: also probably print some line that indicates where you have to click the button maybe <--- arrow to the
# right of the correct line
# TODO: also maybe if they press the value correctly, the board updates instantly like off-clock and replaces
# with a '-' and then board regular update will turn it back

# TODO: make it so that buttons dont spawn every round and maybe its like random # --> spawn but
# the spawn chance is like a function of game difficulty
# maybe make game difficulty a setting

# TODO LOW PRIO: make sure that if i spawn multiple buttons, the buttons don't appear in the same row

class Game:
    difficulty = None
    
    # existing buttons in the game
    existing_buttons = []
    
    def __init__(self, difficulty=3):
        self.difficulty = difficulty

    # corresponds to one game cycle
    def update(self):
        # move all of the existing buttons down one row
        for button in self.existing_buttons:
            button.set_row(button.get_row() + 1)
            
        # if the button exceeds the max row / col, then remove from existing button list
        # TODO: THIS SHOULD ALSO BE WHERE SCORE IS DECREMENTED
        self.existing_buttons = [button for button in self.existing_buttons if not (button.get_row() >= ROWS)]
        
        # then spawn buttons
        self.__button_spawner()

    # helper function that calculates whether to spawns buttons
    def __button_spawner(self):
        # spawn button if there is less buttons than difficutly, for now spawn 1 button call
        if (len(self.existing_buttons) < self.difficulty):
            # spawn button in random column in the 0th row with random lowercase letter key
            self.__spawn_button(row=0, col=random.randint(0,COLS-1), key=(random.choice(string.ascii_lowercase)))

    # helper function to steadily spawn buttons
    def __spawn_button(self, row, col, key):
        b = Button(row=row, col=col, key=key)
        self.existing_buttons.append(b)

    # for getting button locations in main
    def get_buttons(self):
        return self.existing_buttons