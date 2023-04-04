import logging
from game import Game


# Initialize the logging file
logging.basicConfig(filename='game.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

# lots of help from https://realpython.com/pygame-a-primer/#sprite-groups

# all done
# TODO:
# - make the hit zone line diff color and text to indicate
# - make the notes have different symbols on them for motions (rotate is counter clockwise)
# - incorporate the localization
# - fix points
# TODO:
# - make the notes only -1 points if goes through the bottom, don't -1 for 
#   doing incorrect motion for note -- allow players to try again as long as
#   note is not gone yet
#   THIS NEEDS PRINT STATEMENT TOO LIKE "MISSED" OR SOMETHING
# TODO: add point system and text

# not done:
# TODO: Now that IMU info is de-duped, fix Game code to register every message from 
#       IMU mqtt -- includes print messages, there is like spam from multiple different messages
# TODO: draw dots for which region players are in currently from localization
# TODO: graphics could do like motion animations to remove blocks or something


# current state of the game: 
# playable with keyboard or imu for inputs and then also localization running on a computer on different script
# if want to play keyboard and no localization, then in Game.py line 111, change function to process_key instead of
# process_action_location, this makes it so that the action_location is taken care of
# maybe in the future ill implement a setting that is like disable localization for now and it just auto inputs correct
# localization that might be good or just ignores it i mean



# TODO: add sprite for clearing success and bad

# TODO: eventually combine note fall speed and also note update speed
    # currently update is called every update_time ms but also NOTE_FALL_SPEED is a parameter in Note

# should not use on_message from mqtt for imu action because
# it needs to handle actions from the game -- meaning that on_message would need to do Game.__ something or Note.___ which would be
# problematic because we would need to put the game inside on_message which wouldn't work

# eventually will have tutorial or whatever here
# maybe do mygame.tutorial instead when triggered by menu
mygame = Game()
logging.info("GAME: Beginning the main game loop")
mygame.start()