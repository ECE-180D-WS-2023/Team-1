import pygame
from .Settings import *
LIGHT_TIME = 50

class Activity(pygame.sprite.Sprite):
    def __init__(self, play_num):
        super(Activity, self).__init__()
        red_light = pygame.image.load("sprites/light_red.png").convert_alpha()
        blue_light = pygame.image.load("sprites/light_blue.png").convert_alpha()
        green_light = pygame.image.load("sprites/light_green.png").convert_alpha()
        self.cent = (30,50) #TODO Update this
        self.base = red_light 
        self.play_num = 1
        if play_num == 2:
            self.base = blue_light
            self.cent = (800-30,50)
            self.play_num = 2
        self.spike = green_light
        self.active = self.base
        self.surf = self.active
        self.rect = self.surf.get_rect(
            center=self.cent
        )
        self.shake = False
        self.time = 0
        
    def toggle(self):
        self.active = self.spike
        self.time = 0
            #self.shake == True
    
    def update(self):
        self.surf = self.active
        self.time += 1
        if self.time > LIGHT_TIME:
            self.active = self.base
