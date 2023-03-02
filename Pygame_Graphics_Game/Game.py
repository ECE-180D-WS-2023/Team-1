import pygame
from Note import Note, get_lowest_note, SUCCESS, TOO_EARLY, WRONG_KEY
from Settings import NOTE_SPAWN_SPEED_MS, SCREEN_WIDTH, SCREEN_HEIGHT, HIT_ZONE_LOWER, update_time, LETTER_FONT_SIZE, RESULT_FONT_SIZE
from Settings import COLUMN_1, COLUMN_2, COLUMN_3, COLUMN_4
from globals import points
from Text import Text
from pygame.locals import (
    K_q,
    KEYDOWN,
    QUIT,
)

# note that height grows downward, the top left is 0, 0 and bottom right is width, height

class Game():
    # point system when good, increment, when bad, decrement
    def __init__(self):
        pass

    def __calc_points(self, action_input_result):
        global points
        if action_input_result == SUCCESS:
            points += 1
        elif action_input_result == TOO_EARLY or action_input_result == WRONG_KEY:
            points -= 1

    def start(self):
        # setup vars
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        # instantiate sprite groups
        notes = pygame.sprite.Group()
        # text stuff
        # texts = pygame.sprite.Group().add(Text())
        action_input_result_text = Text(text= "Good Luck!")
        points_text = Text(text= "Points: 0", rect= (SCREEN_WIDTH - (SCREEN_WIDTH/6), 70))
        key_font = pygame.font.Font('fonts/arial.ttf', LETTER_FONT_SIZE)
        result_font = pygame.font.Font('fonts/arial.ttf', RESULT_FONT_SIZE)
        points_font = pygame.font.Font('fonts/arial.ttf', RESULT_FONT_SIZE)

        # probably will eventually include other sprites like powerups or chars
        all_sprites = pygame.sprite.Group()


        # note spawning timer
        SPAWNNOTE = pygame.USEREVENT + 1
        pygame.time.set_timer(SPAWNNOTE, int(NOTE_SPAWN_SPEED_MS))

        # received action from imu event
        ACTION = pygame.USEREVENT + 2
        # where the action is stored
        imu_action = None

        # custom note update per speed along with note fall speed
        last_time = pygame.time.get_ticks()

        # variable to store result of key_press attempts
        action_input_result = ""

        # points printing
        global points
    
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
                            action_input_result = lowest_note.process_key(pygame.key.name(event.key))
                            self.__calc_points(action_input_result)
                            points_text.update(text="Points: " + str(points))
                        else:
                            action_input_result = "No Notes Yet!"
                        action_input_result_text.update(text=action_input_result)
                # Check for QUIT event. If QUIT, then set running to false.
                elif event.type == QUIT:
                    running = False
                # spawn note event
                elif event.type == SPAWNNOTE:
                    new_note = Note()
                    notes.add(new_note)
                    all_sprites.add(new_note)
                # if we receive some action from imu
                elif event.type == ACTION:
                    # when handling custom event, reset imu_action_received_flag to False to make sure it doesn't re-trigger
                    lowest_note = get_lowest_note(notes)
                    # FILL IN NOTE'S process_action ONCE ACTIONS ARE KNOWN
                    action_input_result = lowest_note.process_action(imu_action)
                    self.__calc_points(action_input_result)
                    points_text.update(text="Points: " + str(points))

            # FILL IN ONCE ACTIONS ARE KNOWN
            # if action registered by imu, do the event notification and put the action into imu_action
            # when on_message is called, set some global variable imu_action_received_flag to True and set the action to imu_action
            # then when imu_action_received is True, do the custom event post
            # in the loop above, when handling custom event, reset imu_action_received_flag to False to make sure it doesn't re-trigger
            # if (imu_action_received_flag):
                # pygame.event.post(pygame.event.Event(ACTION))
                # imu_action = ___

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

            # include text to indicate hit zone
            # include text to indicate point record
            # include vertical lines to divide into 4 columns/lanes
            pygame.draw.line(screen, (0, 0, 0), (COLUMN_1, 0), (COLUMN_1, SCREEN_HEIGHT))
            pygame.draw.line(screen, (0, 0, 0), (COLUMN_2, 0), (COLUMN_2, SCREEN_HEIGHT))
            pygame.draw.line(screen, (0, 0, 0), (COLUMN_3, 0), (COLUMN_3, SCREEN_HEIGHT))
            pygame.draw.line(screen, (0, 0, 0), (COLUMN_4, 0), (COLUMN_4, SCREEN_HEIGHT))
            # display hit zone
            # horizontal line to indicate hit zone
            pygame.draw.line(screen, (0, 0, 0), (0, HIT_ZONE_LOWER), (SCREEN_WIDTH, HIT_ZONE_LOWER))

            # draw all sprites
            for note in notes:
                screen.blit(note.surf, note.rect)
                screen.blit(key_font.render(note.letter, True, (255,255,255)), note.rect)
            
            # text for key press results
            screen.blit(result_font.render(action_input_result_text.text, True, (0,0,0)), action_input_result_text.rect)
            # text for points
            screen.blit(points_font.render(points_text.text, True, (0,0,0)), points_text.rect)

            # Update the display
            pygame.display.flip()