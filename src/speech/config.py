####################################################################
# Define the words that you want to detect in the format:
# DESIRED_WORD : COMMON_ERROR_LIST
# COMMON_ERROR_LIST is found experimentally using test_microphone.py
#####################################################################
# Make sure that all words in special_words are lowercase
# and str type. The recognizer only outputs in lowercase
#####################################################################

SPECIAL_WORDS = {
    "start" : ["stuart", "stark", "don't"],
    "stop" : ["slob"],
    "pause" : ["pies", "applause", "cause", "because"],
    "continue" : [],
    "player" : ["later", "claire"],
    "enter": ["under", "after"],
    "one" : ["won"],
    "two" : ["to", "too", "do"],
    "i'm excited" : ["i'm actually"],
    "exit" : ["exactly"],
    "quit" : [],
    "back" : [],
    "single" : [],
    "multi" : [],
    "settings" : []
}