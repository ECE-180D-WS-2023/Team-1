import logging
from game import Game
from menu import Menu
#from speech import laptop_speech, config


# Initialize the logging file
logging.basicConfig(filename='game.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

# lots of help from https://realpython.com/pygame-a-primer/#sprite-groups

run = True
while run:
    mymenu = Menu()
    info = mymenu.start()

    # options
    remote_play = info[0]
    num_players = info[1]
    song_title = info[2]
    tutorial = info[3]
    my_team_starts = info[4]
    teamID = info[5]

    mygame = Game()
    if tutorial:
        mygame.tutorial(num_players=num_players, teamID= teamID)
        mymenu.start()
    else:
        logging.info("GAME: Beginning the main game loop")
        mygame.start(num_players=num_players, song_title=song_title, remote_play=remote_play, my_team_starts=my_team_starts, teamID=teamID)
