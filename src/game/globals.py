from .Text import Text
from .Settings import SCREEN_WIDTH
# points need to be decremented by Note also since needs to check when notes fall out of map
# points need to be kept in game too, put here to avoid circular dependency
points = 0

# these need to be used by multiple modules
NUM_PLAYERS = 2

# need these here for Note to update when missed also
points_text = Text(text= "Points: 0", rect= (SCREEN_WIDTH - (SCREEN_WIDTH/8), 70))
action_input_result_text = Text(text= "Good Luck!", rect=(SCREEN_WIDTH - (SCREEN_WIDTH/5) + 15, 20))