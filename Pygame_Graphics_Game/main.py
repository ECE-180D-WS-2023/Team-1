from Game import Game

# lots of help from https://realpython.com/pygame-a-primer/#sprite-groups

# TODO: make the localization outputs int instead of string
    # change the part in Note correct_column() function that checks for correct column
    # change the part in localization_mqtt to directly int() right away the received message payload
    # change in Player the place where player_coords is int()ed, this is no longer needed
# TODO: make a copy of this after ensuring it works to save as good 1p game

# TODO: in scaling to 2p
    # in localization_mqtt, make the distinction between setting player1 and player2 coord and location 
        # "player1_coords player2_coords" as in Player update()
    # then when checking whether the move is correct, need to distinguish between player1 and player2 that made
        # the gesture, possibly set two different events so both ensured that they get processed when gesture'd
        # this involves making action flag for player 1 and also action flag for player 2 then make 2 if statements
        # where the event is created
    # from above, need to pass in player# into process_action_location to make sure the colors match the player's color


# not done:
# TODO: Now that IMU info is de-duped, fix Game code to register every message from 
#       IMU mqtt -- includes print messages, there is like spam from multiple different messages
# TODO: make the text not change if wrong motion
# TODO: make the text not change if wrong lane, for some reason it spams wrong lane
# TODO: draw dots for which region players are in currently from localization
# TODO: graphics could do like motion animations to remove blocks or something
#

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
mygame.start()