"""
Top level localization script
Run this script for localization

Anna Anderson
UID: 105296576
180DA Capstone: Team 1 JAAK
Game: Guitar Hero
This script will be utilized for locating players based on color in accordance with our game.
It utilizes cv2 to process webcam data.
Input: Camera data
Output: Order of players in multiplayer (colors relative to certain regions) or region of single player
"""

from localize_class import localize
import warnings
warnings.filterwarnings("ignore")
local = localize(camera=0, players=2, verbose=True) # set camera=0 if no USB camera, 1 if USB camera
local.detect()