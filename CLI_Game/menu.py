
import time
import pygame

#initialize pygame game
pygame.init()
#from getkey import getkey, keys


#menu outline:
#TODO generate menu with scrolling options (?), be able to select one of them
#TODO maybe print out song name and then they can press left or right arrows to scroll
#TODO print selected song + tempo of selected song

#tempo outline:
#TODO get tempo from song files and add to bank
#TODO audio processing heavy :(


song_bank = {
    "Antihero": 220,
    "American Teenager": 180,
    "Firework": 200,
    "Joanne": 140,
    "Cruel Summer": 170
}

def generate_menu():
    print("Use the arrow keys to browse songs and press enter to select a song!\n")
    i = 0
    while(True):
        songs = list(song_bank)
        user_move = input(songs[i])
        if user_move == "a" and i > 0 :
            i -= 1
        elif user_move == "d" and i < len(songs)-1:
            i += 1
        elif user_move == "s":
            print("Song selected: {}".format(songs[i]))
            return song_bank[songs[i]]
        elif user_move == "q":
            print("Quitting game!")
            break

song = generate_menu()
print(song)