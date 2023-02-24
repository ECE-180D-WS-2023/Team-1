import pygame
from Settings import SCREEN_WIDTH

class Text(pygame.sprite.Sprite):
    def __init__(self, text = "", rect = (SCREEN_WIDTH - (SCREEN_WIDTH/6), 20)):
        self.text = text
        self.rect = rect
    
    def update(self, text):
        self.text = text