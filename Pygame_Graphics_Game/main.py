from Game import Game

# lots of help from https://realpython.com/pygame-a-primer/#sprite-groups

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
# TODO: add sprite for clearing success and bad

# TODO: eventually combine note fall speed and also note update speed
    # currently update is called every update_time ms but also NOTE_FALL_SPEED is a parameter in Note

# should not use on_message from mqtt for imu action because
# it needs to handle actions from the game -- meaning that on_message would need to do Game.__ something or Note.___ which would be
# problematic because we would need to put the game inside on_message which wouldn't work

# eventually will have tutorial or whatever here
# maybe do mygame.tutorial instead when triggered by menu
mygame = Game()
mygame.start()