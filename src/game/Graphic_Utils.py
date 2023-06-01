import pygame
from .Settings import SCREEN_WIDTH, SCREEN_HEIGHT, HIT_ZONE_LOWER, HIGHLIGHT_COLOR
'''
This file outlines the graphics utilities for the game
References:
    - https://stackoverflow.com/questions/6339057/draw-a-transparent-rectangles-and-polygons-in-pygame
'''

# define colors
RED = (255, 182, 193)
BLUE = (137, 207, 240)
PURPLE = (207, 159, 255)
# define rectangle coordinates for each lane
WIDTH = SCREEN_WIDTH/4
HEIGHT= SCREEN_HEIGHT
LEFT1 = 0
LEFT2 = (SCREEN_WIDTH*1)/4
LEFT3 = (SCREEN_WIDTH*2)/4
LEFT4 = (SCREEN_WIDTH*3)/4
L1_RECT = pygame.Rect(LEFT1, 0, WIDTH, HEIGHT-HEIGHT/5) #left, top, width, height
L2_RECT = pygame.Rect(LEFT2, 0, WIDTH, HEIGHT-HEIGHT/5) 
L3_RECT = pygame.Rect(LEFT3, 0, WIDTH, HEIGHT-HEIGHT/5)
L4_RECT = pygame.Rect(LEFT4, 0, WIDTH, HEIGHT-HEIGHT/5)
OUT_OF_AREA = pygame.Rect(0,0,0,0)
lane_dict = {1:L1_RECT, 2:L2_RECT, 3:L3_RECT, 4:L4_RECT, 0:OUT_OF_AREA}

# draw a transparent rectangle
def draw_rect_alpha(surface, color, rect):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)

# draw 
def draw_player_highlights(surface, p1_lane, p2_lane = None):
    if p2_lane != None:
        # both player 1 and player two
        if p1_lane == p2_lane:
            #draw one purple rectangle, return
            draw_rect_alpha(surface, PURPLE, lane_dict[p1_lane])
            return
        else:
            draw_rect_alpha(surface, RED, lane_dict[p1_lane])
            draw_rect_alpha(surface, BLUE, lane_dict[p2_lane])
            return
    else:
        # only player 1
            draw_rect_alpha(surface, RED, lane_dict[p1_lane])
            return