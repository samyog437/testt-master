import pygame
pygame.mixer.init()


pygame.display.init()
pygame.font.init()

tile_types = 33
width = 800
height = 640
level = 0
rows = 16
columns = 150
tile_size = height // rows
scroll_width = 200
camera_scroll = 0
bg_scroll = 0

coin_score = 0
bullet = 20
font = pygame.font.SysFont('commissars', 30)

screen = pygame.display.set_mode((width, height))
bullet_img = pygame.image.load('img/bullet .png').convert_alpha()
box_img = pygame.image.load('img/box.png').convert_alpha()

item_type = {
    'treasure': box_img
}

coin_audio = pygame.mixer.Sound(f'sounds/coin.wav')
enemy_audio = pygame.mixer.Sound(f'sounds/enemy.wav')
die_audio = pygame.mixer.Sound(f'sounds/die.wav')
jump_audio = pygame.mixer.Sound(f'sounds/jump.wav')

images = []
for i in range(tile_types):
    img = pygame.image.load(f'img/tile/{i}.png')
    img = pygame.transform.scale(img, (tile_size, tile_size))
    images.append(img)




