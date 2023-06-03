import pygame
from .Settings import SCREEN_WIDTH, SCREEN_HEIGHT, HIT_ZONE_LOWER
'''
This file outlines the graphics utilities for the game
References:
    - https://stackoverflow.com/questions/6339057/draw-a-transparent-rectangles-and-polygons-in-pygame
'''

# draw a transparent rectangle
def draw_rect_alpha(surface, color, rect):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)