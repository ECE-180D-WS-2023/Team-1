import pygame
from .Settings import PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_Y_COORD, SCREEN_HEIGHT, SCREEN_WIDTH

# define player highlight colors
RED = (255, 182, 193, 127)
BLUE = (137, 207, 240, 127)

# define dimensions for highlight rectangle
WIDTH = SCREEN_WIDTH/4
HEIGHT= SCREEN_HEIGHT - SCREEN_HEIGHT/5

class Player(pygame.sprite.Sprite):
    player_num = 0

    def __init__(self, player_num):
        super(Player, self).__init__()
        self.player_num = player_num

        self.player_localization_pos = 0

        # highlight rectangle
        self.highlight_rec = pygame.Rect(0,0,0,0)
        
        self.surf = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))

        # if player 1 then red square, if player 2 then blue square
        if (player_num == 1):
            self.highlight_color = RED
            red_player =  pygame.image.load("sprites/red_note_32.png").convert_alpha()
            self.surf = red_player
            self.rect = self.surf.get_rect(
                center=(
                    0, 0
                )
            )
        elif (player_num == 2):
            self.highlight_color = BLUE
            blue_player =  pygame.image.load("sprites/blue_note_32.png").convert_alpha()
            self.surf = blue_player
            self.rect = self.surf.get_rect(
                center=(
                    0, 0
                )
            )
    
    # need to update according to player num
    # this can be deleted once tested that localization still works 5/24/2023
    """
    def update(self):
        if (self.player_num == 1):
            self.rect = self.surf.get_rect(
                center = (
                    ((640-(mqtt_lib.localization_mqtt.player1_coords))/640)*SCREEN_WIDTH, 
                    PLAYER_Y_COORD
                )
            )
        elif (self.player_num == 2):
            self.rect = self.surf.get_rect(
                center = (
                    ((640-int(mqtt_lib.localization_mqtt.player2_coords))/640)*SCREEN_WIDTH, 
                    PLAYER_Y_COORD
                )
            )
    """
    
    def update_player_pos(self, player_num, coords):
        if (player_num == 1 and self.player_num == 1):
            self.rect = self.surf.get_rect(
                center = (
                    ((640-(coords))/640)*SCREEN_WIDTH, 
                    PLAYER_Y_COORD
                )
            )
            # define player 1 highlight rectangle
            x, _, _, _ = self.rect
            new_x = x - 84
            if new_x < 0:
                new_x = 0
            if new_x > SCREEN_WIDTH:
                new_x = SCREEN_WIDTH
            self.highlight_rec = pygame.Rect(new_x, 0, WIDTH, HEIGHT)
        elif (self.player_num == 2 and self.player_num == 2):
            self.rect = self.surf.get_rect(
                center = (
                    ((640-int(coords))/640)*SCREEN_WIDTH, 
                    PLAYER_Y_COORD
                )
            )
            # define player 2 highlight rectangle
            x, _, _, _ = self.rect
            new_x = x - 82
            if new_x < 0:
                new_x = 0
            if new_x > SCREEN_WIDTH:
                new_x = SCREEN_WIDTH
            self.highlight_rec = pygame.Rect(new_x, 0, WIDTH, HEIGHT)