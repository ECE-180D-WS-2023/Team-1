import pygame

class Progress_Bar():
    def __init__(self, x, y, width, height, progress = 0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.progress = progress

    def draw(self, window, outline_color, inner_color):
        # Create outline rectangle with rounded ends
        pygame.draw.rect(window, outline_color, (self.x + self.height // 2, self.y, self.width - self.height, self.height))
        pygame.draw.circle(window, outline_color, (self.x + self.height // 2, self.y + self.height // 2), self.height // 2)
        pygame.draw.circle(window, outline_color, (self.x + self.width - self.height // 2, self.y + self.height // 2), self.height // 2)

        # Create inner rectangle with rounded ends
        pygame.draw.rect(window, inner_color, (self.x + self.height // 2, self.y, (self.width - self.height) * (self.progress / 100), self.height))
        if self.progress > 0:
            pygame.draw.circle(window, inner_color, (self.x + self.height // 2, self.y + self.height // 2), self.height // 2)
        
    def set_progress(self, progress):
        self.progress = progress