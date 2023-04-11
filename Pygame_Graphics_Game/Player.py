import pygame
import localization_mqtt
from Settings import PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_Y_COORD, SCREEN_HEIGHT, SCREEN_WIDTH

class Player(pygame.sprite.Sprite):
    player_num = 0

    def __init__(self, player_num):
        super(Player, self).__init__()
        self.player_num = player_num

        self.surf = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))

        # if player 1 then red square, if player 2 then blue square
        if (player_num == 1):
            self.surf.fill((255, 0, 0))
            self.rect = self.surf.get_rect(
                center=(
                    0, 0
                )
            )
        elif (player_num == 2):
            self.surf.fill((0, 255, 0))
            self.rect = self.surf.get_rect(
                center=(
                    0, 0
                )
            )
    
    # need to update according to player num
    def update(self):
        if (self.player_num == 1):
            self.rect = self.surf.get_rect(
                center = (
                    ((640-int(localization_mqtt.player1_coords))/640)*SCREEN_WIDTH, 
                    PLAYER_Y_COORD
                )
            )
        elif (self.player_num == 2):
            self.rect = self.surf.get_rect(
                center = (
                    ((640-int(localization_mqtt.player2_coords))/640)*SCREEN_WIDTH, 
                    PLAYER_Y_COORD
                )
            )