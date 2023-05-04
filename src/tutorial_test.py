import logging
from game import Game
from menu import Menu
#from speech import laptop_speech, config


# Initialize the logging file
logging.basicConfig(filename='game.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

# lots of help from https://realpython.com/pygame-a-primer/#sprite-groups

# TODO: eventually combine note fall speed and also note update speed
    # currently update is called every update_time ms but also NOTE_FALL_SPEED is a parameter in Note


# eventually will have tutorial or whatever here
# maybe do mygame.tutorial instead when triggered by menu
mygame = Game()
logging.info("GAME: Beginning the main game loop")
mygame.tutorial(num_players=2)