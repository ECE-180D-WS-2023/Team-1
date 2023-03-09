from Settings_cp import ROWS, COLS

# how many blank lines between each grid print
FILLER = 7

class Grid:
    num_rows = ROWS
    num_cols = COLS
    grid = []

    def __init__(self, num_fill = False, num_rows = ROWS, num_cols=COLS):
        # set # rows and cols to inputted value or default
        self.num_rows = num_rows
        self.num_cols = num_cols

        self.grid = [ ['.']*self.num_cols for i in range(self.num_rows)] 

        if(num_fill == True):
            for row in range(self.num_rows):
                for col in range(self.num_cols):
                    self.grid[row][col] = str(col)

    # resets the grid to all . -- do this before updating new points
    def reset_grid(self):
        self.grid = [ ['.']*self.num_cols for i in range(self.num_rows)]

    def get_grid_point(self, row, col):
        return self.grid[row][col]

    def get_grid(self):
        return self.grid

    def set_point(self, row, col, val):
        self.grid[row][col] = val
        return

    def print_grid(self):
        for i in range(FILLER):
            print("")
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                print(self.grid[row][col] + " ", end="")
            print("\n", end="")

#g = Grid(num_fill = True)
#g.print_grid()
#print(g.get_grid_point(2,3))
#print(g.get_grid())