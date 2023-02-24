import pygame
from Note import Note, get_lowest_note, SUCCESS, TOO_EARLY, WRONG_KEY
from Settings import NOTE_SPAWN_SPEED_MS, SCREEN_WIDTH, SCREEN_HEIGHT, HIT_ZONE_LOWER, update_time, LETTER_FONT_SIZE, RESULT_FONT_SIZE
from Text import Text
from pygame.locals import (
    K_q,
    KEYDOWN,
    QUIT,
)

# TODO: eventually combine note fall speed and also note update speed
    # currently update is called every update_time ms but also NOTE_FALL_SPEED is a parameter in Note
# TODO: add hit zone text
# TODO: add point system and text
# TODO: add sprite for clearing success and bad

# note that height grows downward, the top left is 0, 0 and bottom right is width, height

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# instantiate sprite groups
notes = pygame.sprite.Group()
# text stuff
# texts = pygame.sprite.Group().add(Text())
key_press_result_text = Text()
key_font = pygame.font.Font('fonts/arial.ttf', LETTER_FONT_SIZE)
result_font = pygame.font.Font('fonts/arial.ttf', RESULT_FONT_SIZE)

# probably will eventually include other sprites like powerups or chars
all_sprites = pygame.sprite.Group()


# note spawning timer
SPAWNNOTE = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWNNOTE, int(NOTE_SPAWN_SPEED_MS))

# custom note update per speed along with note fall speed
last_time = pygame.time.get_ticks()

# variable to store result of key_press attempts
key_press_result = ""

# Variable to keep the main loop running
running = True
while running:
    for event in pygame.event.get():
        # check if q is pressed then leave
        if event.type == KEYDOWN:
            if event.key == K_q:
                running = False
            else:
                # calculate which note is the lowest and then process key press accordingly based
                # on that note's letter
                if (notes):
                    lowest_note = get_lowest_note(notes)
                    key_press_result = lowest_note.process_key(pygame.key.name(event.key))
                else:
                    key_press_result = "No Notes Yet!"
                key_press_result_text.update(text=key_press_result)
        # Check for QUIT event. If QUIT, then set running to false.
        elif event.type == QUIT:
            running = False
        # spawn note event
        elif event.type == SPAWNNOTE:
            new_note = Note()
            notes.add(new_note)
            all_sprites.add(new_note)


    # update note positions
    if (pygame.time.get_ticks() - last_time > update_time):
        notes.update()
        last_time = pygame.time.get_ticks()

    # Fill the screen with black
    screen.fill((255, 255, 255))

    # Get all of the keys currently pressed
    # pressed_keys = pygame.key.get_pressed()
    # process pressed_keys
    # get lowest note and process the key that was pressed
    # get_lowest_note(notes).process_key(pygame.key.name(pressed_keys.key))

    # draw all sprites
    for note in notes:
        screen.blit(note.surf, note.rect)
        screen.blit(key_font.render(note.letter, True, (255,255,255)), note.rect)
    
    screen.blit(result_font.render(key_press_result_text.text, True, (0,0,0)), key_press_result_text.rect)

    # display hit zone
    # horizontal line to indicate hit zone
    pygame.draw.line(screen, (0, 0, 0), (0, HIT_ZONE_LOWER), (SCREEN_WIDTH, HIT_ZONE_LOWER))
    
    # include text to indicate hit zone
    

    # Update the display
    pygame.display.flip()