import pygame
import random
from pygame.locals import (
    K_q,
    KEYDOWN,
    QUIT,
)

# note that height grows downward, the top left is 0, 0 and bottom right is width, height

bpm = 60

NOTE_FALL_SPEED = 1
NOTE_SPAWN_SPEED_MS = ((1/bpm)*60)*1000

# screen width and height
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Note size
NOTE_WIDTH = 40
NOTE_HEIGHT = 40

# HIT ZONE (lower bound) HEIGHT -- height grows downward
HIT_ZONE_LOWER = SCREEN_HEIGHT-(SCREEN_HEIGHT/5)

# Note class for falling buttons
class Note(pygame.sprite.Sprite):
    def __init__(self):
        super(Note, self).__init__()
        self.surf = pygame.Surface((NOTE_WIDTH, NOTE_HEIGHT))
        self.surf.fill((0, 100, 100))
        self.rect = self.surf.get_rect(
            center=(
                random.randint(NOTE_WIDTH/2, SCREEN_WIDTH-(NOTE_WIDTH/2)),
                0
            )
        )

    # Move the note downwards based on fall speed
    # Remove the note when it passes the bottom edge of the screen
    def update(self):
        self.rect.move_ip(0, NOTE_FALL_SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# instantiate sprite groups
notes = pygame.sprite.Group()
# probably will eventually include other sprites like powerups or chars
all_sprites = pygame.sprite.Group()

# note spawning
SPAWNNOTE = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWNNOTE, int(NOTE_SPAWN_SPEED_MS))

# Variable to keep the main loop running
running = True
while running:
    for event in pygame.event.get():
        # check if q is pressed then leave
        if event.type == KEYDOWN:
            if event.key == K_q:
                running = False
        # Check for QUIT event. If QUIT, then set running to false.
        elif event.type == QUIT:
            running = False
        # spawn note event
        elif event.type == SPAWNNOTE:
            new_note = Note()
            notes.add(new_note)
            all_sprites.add(new_note)

    # update note positions
    notes.update()

    # Fill the screen with black
    screen.fill((255, 255, 255))

    # Get all of the keys currently pressed
    pressed_keys = pygame.key.get_pressed()
    # process pressed_keys
    

    # draw all sprites
    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)

    # display hit zone
    # horizontal line to indicate hit zone
    pygame.draw.line(screen, (0, 0, 0), (0, HIT_ZONE_LOWER), (SCREEN_WIDTH, HIT_ZONE_LOWER))
    # text to indicate hit zone
    

    # Update the display
    pygame.display.flip()