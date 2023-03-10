import pygame
# note that height grows downward, the top left is 0, 0 and bottom right is width, height

# controls how much the note falls per refresh
NOTE_FALL_SPEED = 1
# time in between refresh game
update_time = 3

# time between each motion register
time_between_motion = 0
# MQTT CALIBRATION TIME
MQTT_CALIBRATION_TIME = 10000

# LOCALIZATION CALIBRATION TIME
LOCALIZATION_CALIBRATION_TIME = 1000

BPM = 30
NOTE_SPAWN_SPEED_MS = ((1/BPM)*60)*1000

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

# list of available keyboard clicks
KEYS = 'ulfr'

# HIT ZONE (lower bound) HEIGHT -- height grows downward
HIT_ZONE_LOWER = SCREEN_HEIGHT-(SCREEN_HEIGHT/5)

COLUMN_1 = SCREEN_WIDTH/5
COLUMN_2 = (SCREEN_WIDTH*2)/5
COLUMN_3 = (SCREEN_WIDTH*3)/5
COLUMN_4 = (SCREEN_WIDTH*4)/5