import pygame
import random
from Settings import NOTE_FALL_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT, NOTE_WIDTH, NOTE_HEIGHT, KEYS, HIT_ZONE_LOWER
from Settings import COLUMN_1, COLUMN_2, COLUMN_3, COLUMN_4

SUCCESS = "Nice!"
TOO_EARLY = "Too Early!"
WRONG_KEY = "Wrong Key!"

COLUMN_COLOR_1 = (100, 0 , 0)
COLUMN_COLOR_2 = (0, 100 , 0)
COLUMN_COLOR_3 = (0, 0 , 100)
COLUMN_COLOR_4 = (200, 200 , 0)

# Note class for falling buttons
class Note(pygame.sprite.Sprite):
    def __init__(self):
        super(Note, self).__init__()
        self.lane = random.choice([COLUMN_1, COLUMN_2, COLUMN_3, COLUMN_4])
        self.surf = pygame.Surface((NOTE_WIDTH, NOTE_HEIGHT))
        # color in the square according to its lane
        if (self.lane == COLUMN_1):
            self.surf.fill(COLUMN_COLOR_1)
        elif (self.lane == COLUMN_2):
            self.surf.fill(COLUMN_COLOR_2)
        elif (self.lane == COLUMN_3):
            self.surf.fill(COLUMN_COLOR_3)
        elif (self.lane == COLUMN_4):
            self.surf.fill(COLUMN_COLOR_4)
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

    # Move the note downwards based on fall speed
    # Remove the note when it passes the bottom edge of the screen
    def update(self):
        self.rect.move_ip(0, NOTE_FALL_SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
    
    # use on key that is lowest
    # returns the result of the key press back to main
    def process_key(self, pressed_keys):
        if (pressed_keys == self.char and self.rect.bottom > HIT_ZONE_LOWER):
            self.kill()
            return SUCCESS
        elif pressed_keys == self.char and not self.rect.bottom > HIT_ZONE_LOWER:
            self.kill()
            return TOO_EARLY
        else:
            self.kill()
            return WRONG_KEY

# calculates lowest key and returns that note
def get_lowest_note(notes):
    lowest_note = max(notes, key=lambda x: x.rect.top)
    return lowest_note