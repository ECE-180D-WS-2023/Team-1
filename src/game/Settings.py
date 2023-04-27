import pygame
# note that height grows downward, the top left is 0, 0 and bottom right is width, height

# controls how much the note falls per refresh
NOTE_FALL_SPEED = 1
# time in between refresh game
note_update_time = 3

# time between each motion register
time_between_motion = 0
# MQTT CALIBRATION TIME
MQTT_CALIBRATION_TIME = 1000

# LOCALIZATION CALIBRATION TIME
LOCALIZATION_CALIBRATION_TIME = 1000

# screen width and height on laptop
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
# screen width and height on pc
#SCREEN_WIDTH = 1500
#SCREEN_HEIGHT = 840

# Note size on laptop
NOTE_WIDTH = 40
NOTE_HEIGHT = 40
#NOTE_WIDTH = 80
#NOTE_HEIGHT = 80

# Letter font size
LETTER_FONT_SIZE = NOTE_WIDTH
# Result print font size
RESULT_FONT_SIZE = int(NOTE_WIDTH/2)
# hitzone text font size
HITZONE_FONT_SIZE = int(NOTE_WIDTH/4)
# paused screen font size
PAUSED_FONT_SIZE = int(NOTE_WIDTH*2)

# list of available keyboard clicks
KEYS = 'ulfr'

# HIT ZONE (lower bound) HEIGHT -- height grows downward
HIT_ZONE_LOWER = SCREEN_HEIGHT-(SCREEN_HEIGHT/5)

COLUMN_1 = SCREEN_WIDTH/8
COLUMN_2 = (SCREEN_WIDTH*3)/8
COLUMN_3 = (SCREEN_WIDTH*5)/8
COLUMN_4 = (SCREEN_WIDTH*7)/8

LINE_COLUMN_1 = SCREEN_WIDTH/4
LINE_COLUMN_2 = (SCREEN_WIDTH*1)/4
LINE_COLUMN_3 = (SCREEN_WIDTH*2)/4
LINE_COLUMN_4 = (SCREEN_WIDTH*3)/4


# PLAYER
PLAYER_WIDTH = NOTE_WIDTH*(8/10)
PLAYER_HEIGHT = NOTE_HEIGHT*(8/10)
PLAYER_Y_COORD = SCREEN_HEIGHT - (SCREEN_HEIGHT/7)
PLAYER_1_COLOR = (255, 0, 0)
PLAYER_2_COLOR = (0, 0, 255)