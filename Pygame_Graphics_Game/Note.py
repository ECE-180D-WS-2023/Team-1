import pygame
import random
from Settings import NOTE_FALL_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT, NOTE_WIDTH, NOTE_HEIGHT, KEYS, HIT_ZONE_LOWER
from Settings import COLUMN_1, COLUMN_2, COLUMN_3, COLUMN_4
import globals

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

#COLOR_2 = (144, 238, 144) #g
#COLOR_3 = (173, 216, 230) #b
#COLOR_4 = (255,255,102) #y

# Note class for falling buttons
class Note(pygame.sprite.Sprite):
    def __init__(self):
        super(Note, self).__init__()
        self.lane = random.choice([COLUMN_1, COLUMN_2, COLUMN_3, COLUMN_4])
        
        self.surf = pygame.Surface((NOTE_WIDTH, NOTE_HEIGHT))

        self.color = ""
        # randomly generate either 1 or 2 for color
        if (random.randint(1,2) == 1):
            self.color = COLOR_1
        else:
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
        
        # the letter assigned to note, randomly generated
        self.char = random.choice(KEYS)
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
        # if the note goes off the edge, return too_late to indicate that the note ran out
        if self.rect.top > SCREEN_HEIGHT:
            #print(points)
            globals.points -= 1
            globals.action_input_result_text.update(text="Missed!")
            self.kill()
    

    # for keyboard clicking processing
    # use on key that is lowest
    # returns the result of the key press back to main
    # if we only have keyboard
    def process_key(self, pressed_keys):
        # if the key press is correct and is also in the hit zone
        if pressed_keys == self.char and self.rect.bottom > HIT_ZONE_LOWER:
            self.kill()
            return SUCCESS
        elif pressed_keys == self.char and not self.rect.bottom > HIT_ZONE_LOWER:
            return TOO_EARLY
        else:
            return WRONG_KEY

    # if we have <imu or keyboard> AND <localization>
    def process_action_location(self, action, location, player_num):
        # check that the player cleared the correct color
        # if the key press is correct and is also in the hit zone AND also in the correct column
        if action == self.char and self.rect.bottom > HIT_ZONE_LOWER and self.correct_column(location) and self.correct_color(player_num):
            self.kill()
            return SUCCESS
        elif not self.correct_color(player_num):
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

# calculates lowest key and returns that note
def get_lowest_note(notes):
    lowest_note = max(notes, key=lambda x: x.rect.top)
    return lowest_note