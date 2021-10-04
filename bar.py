from basics import *

class Bar(pygame.sprite.Sprite):
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health
        pygame.draw.rect(screen, 'black', (self.x -2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, 'red', (self.x, self.y , 150, 20))
        pygame.draw.rect(screen, 'gray', (self.x, self.y , 150 * (health/self.max_health), 20))











