import pygame
import random
import math
from .Settings import NOTE_FALL_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT, NOTE_WIDTH, NOTE_HEIGHT, KEYS, HIT_ZONE_LOWER
from .Settings import COLUMN_1, COLUMN_2, COLUMN_3, COLUMN_4
from . import globals

SUCCESS = "Nice!"
TOO_EARLY = "Too Early!"
WRONG_KEY = "Wrong Motion!"
WRONG_LANE = "Wrong Lane!"
WRONG_COLOR = "Wrong Color!"

TOO_LATE = "Too Late!"

# we want only r and b column colors now
COLOR_1 = (255, 204, 203) #r
COLOR_2 = (173, 216, 230) #b
COLOR_3 = COLOR_1
COLOR_4 = COLOR_2

# when gesture incorrect, shake the note
SHAKE_AMPLITUDE = 10
SHAKE_PERIOD = 4
INCORRECT_SHAKE_TIME = 20*math.pi

#COLOR_2 = (144, 238, 144) #g
#COLOR_3 = (173, 216, 230) #b
#COLOR_4 = (255,255,102) #y

# Note class for falling buttons
class Note(pygame.sprite.Sprite):
    def __init__(self, color=None, lane=None, char=None):
        super(Note, self).__init__()
        self.alive = True
        self.shake_time = 0

        if lane == None:
            self.lane = random.choice([COLUMN_1, COLUMN_2, COLUMN_3, COLUMN_4])
        elif lane == 1:
            self.lane = COLUMN_1
        elif lane == 2:
            self.lane = COLUMN_2
        elif lane == 3:
            self.lane = COLUMN_3
        else:
            self.lane = COLUMN_4
        
        self.surf = pygame.Surface((NOTE_WIDTH, NOTE_HEIGHT))

        self.color = ""
        
        # if 1 player, the color will always be red
        if color == None:
            if (globals.NUM_PLAYERS == 1):
                self.color = COLOR_1
            # if 2 player, the color will be red/blue random
            elif (globals.NUM_PLAYERS == 2):
                # randomly generate either 1 or 2 for color
                if (random.randint(1,2) == 1):
                    self.color = COLOR_1
                else:
                    self.color = COLOR_2
        elif color == 1:
            self.color = COLOR_1
        elif color == 2:
            self.color = COLOR_2

        # color in the square according to its lane
        self.surf.fill(self.color)

        # self.surf.fill((0, 100, 100)) # default color
        self.rect = self.surf.get_rect(
            center=(
                # random.randint(NOTE_WIDTH/2, SCREEN_WIDTH-(NOTE_WIDTH/2)), # for randomly on screen
            self.lane, 0
            )
        )
        self.init_x = self.rect.x
        
        if char == None:
        # the letter assigned to note, randomly generated
            self.char = random.choice(KEYS)
        else:
            self.char = char
        self.letter = self.char

        # give the correct image accordingly
        if (self.char == 'u'):
            up_image = pygame.image.load("sprites/up_40.png")
            self.surf.blit(up_image, (0, 0))
        elif (self.char == 'l'):
            left_image = pygame.image.load("sprites/left_40.png")
            self.surf.blit(left_image, (0, 0))
        elif (self.char == 'f'):
            forward_image = pygame.image.load("sprites/cross_40.png")
            self.surf.blit(forward_image, (0, 0))
        elif (self.char == 'r'):
            rotate_image = pygame.image.load("sprites/rotate_40.png")
            self.surf.blit(rotate_image, (0, 0))
        

    # Move the note downwards based on fall speed
    # Remove the note when it passes the bottom edge of the screen
    def update(self):
        self.rect.move_ip(0, NOTE_FALL_SPEED)

        # for shaking when incorrect
        if self.shake_time > 0:
            self.shake_time -= 1
            self.rect.x += int(SHAKE_AMPLITUDE*math.sin(((2*math.pi)/SHAKE_PERIOD) * self.shake_time))
        else:
            self.rect.x = self.init_x

        # if the note goes off the edge, return too_late to indicate that the note ran out
        if self.rect.top > SCREEN_HEIGHT:
            #print(points)
            if self.alive:
                globals.points -= 1
                globals.action_input_result_text.update(text="Missed!")
            self.kill()
    

    # for keyboard clicking processing
    # use on key that is lowest
    # returns the result of the key press back to main
    # if we only have keyboard
    def process_key(self, pressed_keys):
        # if the key press is correct and is also in the hit zone
        if self.alive:
            if pressed_keys == self.char and self.rect.bottom > HIT_ZONE_LOWER:
                self.alive = False
                self.__note_cleared()
                return SUCCESS
            # if incorrect
            else: 
                self.shake_time = INCORRECT_SHAKE_TIME
                if pressed_keys == self.char and not self.rect.bottom > HIT_ZONE_LOWER:
                    return TOO_EARLY
                else:
                    return WRONG_KEY

    # if we have <imu or keyboard> AND <localization>
    def process_action_location(self, action, location, player_num):
        # check that the player cleared the correct color
        # if the key press is correct and is also in the hit zone AND also in the correct column
        if action == self.char and self.rect.bottom > HIT_ZONE_LOWER and self.correct_column(location) and self.correct_color(player_num):
            self.alive = False
            self.__note_cleared()
            return SUCCESS
        # if incorrect
        else:
            self.shake_time = INCORRECT_SHAKE_TIME
            if not self.correct_color(player_num):
                return WRONG_COLOR
            elif not self.correct_column(location):
                return WRONG_LANE
            elif action == self.char and not self.rect.bottom > HIT_ZONE_LOWER:
                return TOO_EARLY
            else:
                return WRONG_KEY
    
    # checks if the player is in the same column as the note
    # note that the input column should be a string, either "1", "2", "3", or "4"
    # this is based on what localization script outputs
    def correct_column(self, column):
        if self.lane == COLUMN_1 and column == 1:
            return True
        if self.lane == COLUMN_2 and column == 2:
            return True
        if self.lane == COLUMN_3 and column == 3:
            return True
        if self.lane == COLUMN_4 and column == 4:
            return True
        return False

    def correct_color(self, player_num):
        if player_num == 1:
            if self.color == COLOR_1 or self.color == COLOR_3:
                return True
        elif player_num == 2:
            if self.color == COLOR_2 or self.color == COLOR_4:
                return True
        return False
    
    def __note_cleared(self):
        self.surf.fill(pygame.Color('white'))
        check_mark_image = pygame.image.load("sprites/check_mark2_40.png")
        self.surf.blit(check_mark_image, (0, 0))

# calculates lowest living note and returns that note
def get_lowest_note(notes):
    lowest_note = max(notes, key=lambda x: x.rect.top if x.alive else -1)
    return lowest_note