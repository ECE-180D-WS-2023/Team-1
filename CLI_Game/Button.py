# for holding the class that should represent button object
# there should be another class that should have the game logic where buttons are created

class Button:
    # Button has 3 properties, row its in, column its in, and the key that needs to be pressed to clear it
    row = None
    col = None
    key = None
    
    def __init__(self, row, col, key):
        self.row = row
        self.col = col
        self.key = key
    
    # getters
    def get_location(self):
        return self.row, self.col
    def get_col(self):
        return self.col
    def get_row(self):
        return self.row
    def get_key(self):
        return self.key
    
    # setters
    def set_col(self, col):
        self.col = col
    def set_row(self, row): # maybe we eventually will have row swapping
        self.row = row