import pygame
import localization_mqtt
from Settings import PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_Y_COORD, SCREEN_HEIGHT, SCREEN_WIDTH

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.surf.fill((255, 0, 0))
        self.rect = self.surf.get_rect(
            center=(
                0, 0
            )
        )
    
    def update(self):
        # print(localization_mqtt.player_coords)
        self.rect = self.surf.get_rect(
            center = (
                ((640-int(localization_mqtt.player_coords))/640)*SCREEN_WIDTH, 
                PLAYER_Y_COORD
            )
        )