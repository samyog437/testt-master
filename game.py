import os
import sqlite3

from bar import *
import random
import csv
import login
pygame.init()
pygame.font.init()

clock = pygame.time.Clock()
fps = 60
keys = pygame.key.get_pressed()

turn_left = False
turn_right = False

pygame.display.set_caption("Runnin")

sun_img = pygame.image.load('img/sun.png')
sun_img = pygame.transform.scale(sun_img, (tile_size, tile_size))
bg_img = pygame.image.load('img/sky.png').convert_alpha()
bg_img = pygame.transform.scale(bg_img, (width, height))
pine1_img = pygame.image.load('img/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/sky_cloud.png').convert_alpha()

restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()

score_coin_img = pygame.image.load('img/tile/32.png').convert_alpha()
coin_img = pygame.transform.scale(score_coin_img, (25, 25))

bullet_count = pygame.transform.scale(bullet_img, (25, 25))


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def restart():
    ammo_group.empty()
    danger_group.empty()
    decoration_group.empty()
    treasure_group.empty()
    exit_group.empty()
    enemy_group.empty()

    data = []
    for row in range(rows):
        r = [-1] * columns
        data.append(r)
    return data


def draw_bg():
    s_width = sky_img.get_width()
    for x in range(5):
        screen.blit(bg_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * s_width) - bg_scroll * 0.6, height - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * s_width) - bg_scroll * 0.7, height - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * s_width) - bg_scroll * 0.8, height - pine2_img.get_height()))


class Character(pygame.sprite.Sprite):

    def __init__(self, char_type, x, y, vel, bullet):
        self.index = 0
        self.char_type = char_type
        self.vel = vel

        self.img_list = []
        self.frame_index = 0
        self.state = 0
        self.update_time = pygame.time.get_ticks()

        self.shoot_timer = 0
        self.bullet = bullet
        self.initial_bullet = bullet

        img_state = ['idle', 'run', 'jump', 'dead']
        for state in img_state:
            images = []
            num_of_img = len(os.listdir(f'img/{self.char_type}/{state}'))

            for num in range(num_of_img):
                img = pygame.image.load(f'img/{self.char_type}/{state}/{num}.png').convert_alpha()
                img = pygame.transform.scale(img, (40, 80)).convert_alpha()
                images.append(img)
            self.img_list.append(images)

        self.image = self.img_list[self.state][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.jump_vel = 0
        self.jump = False
        self.direction = 1
        self.flip = False
        self.jumping = True

        self.alive = True
        self.health = 100
        self.max_health = self.health
        self.health_timer = 0
        self.decrease = False

        self.mask = pygame.mask.from_surface(self.image)
        self.move_timer = 0
        self.stop = False

    def character_state(self):
        change_time = 100
        self.image = self.img_list[self.state][self.frame_index]

        if pygame.time.get_ticks() - self.update_time > 100:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        if self.frame_index >= len(self.img_list[self.state]):
            if self.state == 3:
                self.frame_index = len(self.img_list[self.state]) - 1
            else:
                self.frame_index = 0

    def check_state(self, new_state):
        if new_state != self.state:
            self.state = new_state
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def shoot(self):
        if self.shoot_timer == 0 and self.bullet > 0:
            self.shoot_timer = 20
            ammo = Ammo(self.rect.centerx + (self.rect.size[0] * self.direction), self.rect.centery,
                        self.direction)
            ammo_group.add(ammo)

            self.bullet -= 1

    def update(self):
        self.character_state()
        self.death()

        if self.shoot_timer > 0:
            self.shoot_timer -= 1

    def move(self, turn_left, turn_right):
        camera_scroll = 0
        change_x = 0
        change_y = 0

        # turning
        if turn_right:
            change_x = self.vel
            self.flip = False
            self.direction = 1
        elif turn_left:
            change_x = -self.vel
            self.flip = True
            self.direction = -1

        # falling

        if self.jump == True and self.jumping == False:
            self.jump_vel = -23
            self.jump = False
            self.jumping = True

        self.jump_vel += 1
        if self.jump_vel > 10:
            self.jump_vel
        change_y += self.jump_vel

        for objects in world.collision_tiles:
            # getting rect by[1]
            if objects[1].colliderect(self.rect.x + change_x, self.rect.y, self.width, self.height):
                change_x = 0

                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_timer = 0

            if objects[1].colliderect(self.rect.x, self.rect.y + change_y, self.width, self.height):
                if self.jump_vel < 0:
                    self.jump_vel = 0
                    change_y = objects[1].bottom - self.rect.top

                elif self.jump_vel >= 0:
                    self.jump_vel = 0
                    self.jumping = False
                    change_y = objects[1].top - self.rect.bottom

        # danger group
        if pygame.sprite.spritecollide(self, danger_group, False):
            self.health = 0

        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        if pygame.sprite.spritecollide(self, enemy_group, False):
            self.health -= 0.7

        # off the map
        if self.rect.bottom > height:
            self.health = 0

        if self.char_type == 'player':
            if self.rect.left + change_x < -15 or self.rect.right + change_x > width:
                change_x = 0

        self.rect.x += change_x
        self.rect.y += change_y

        if self.char_type == 'player':
            # scroll left or right
            if (self.rect.right > width / 4 and self.direction > 0) or (
                    self.rect.left < width - width / 4 and self.direction < 0):
                self.rect.x -= change_x
                camera_scroll = - change_x
        return camera_scroll, level_complete

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

    def death(self):
        if self.health <= 0:
            self.health = 0
            self.vel = 0
            self.alive = False

            self.check_state(3)

    def enemy_movement(self):
        if self.alive and player.alive:
            if self.stop == False and random.randint(1, 200) == 2:
                self.check_state(0)
                self.stop = True
                self.stop_timer = 50

            else:
                if self.stop == False:

                    if self.direction == 1:
                        ene_right = True
                    else:
                        ene_right = False
                    ene_left = not ene_right
                    self.move(ene_left, ene_right)
                    self.check_state(1)
                    self.move_timer += 1

                    # how far enemies walk
                    if self.move_timer > tile_size:
                        self.direction *= -1
                        self.move_timer *= -1
                else:
                    self.stop_timer -= 1
                    if self.stop_timer <= 0:
                        self.stop = False
        self.rect.x += camera_scroll


class Ammo(pygame.sprite.Sprite):
    score = 0

    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)  # inherit from sprite
        self.vel = 5
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        score = 0
        self.rect.x += (self.direction * self.vel) + camera_scroll

        if self.rect.right > width or self.rect.right < 0:
            self.kill()

        if pygame.sprite.spritecollide(player, ammo_group, False):
            if player.alive:
                player.health -= 20
                self.kill()

        if pygame.sprite.spritecollide(self, enemy_group, False):
            self.kill()

        collided_enemy = pygame.sprite.spritecollideany(self, enemy_group)
        if collided_enemy:
            enemy_audio.play()
            collided_enemy.kill()


class Level:
    def __init__(self):
        self.collision_tiles = []

    def game_data(self, layout):
        self.level_length = len(layout[0])
        # iterate through csv files
        for i, row in enumerate(layout):
            for j, tile in enumerate(row):
                if tile >= 0:
                    img = images[tile]
                    img_rect = img.get_rect()
                    # positions on the screen
                    img_rect.x = j * tile_size
                    img_rect.y = i * tile_size

                    # tile data

                    tile_data = (img, img_rect)

                    if 0 <= tile <= 21:
                        self.collision_tiles.append(tile_data)
                    elif 22 <= tile <= 25:
                        deco = Deco(img, j * tile_size, i * tile_size)
                        decoration_group.add(deco)
                    elif tile == 26:
                        treasure = Treasure('treasure', j * tile_size, i * tile_size)
                        treasure_group.add(treasure)
                    elif tile == 27 or tile == 28:
                        danger = Danger(img, j * tile_size, i * tile_size)
                        danger_group.add(danger)
                    elif tile == 29:
                        enemy = Blob(img, j * tile_size, i * tile_size)
                        enemy_group.add(enemy)
                    elif tile == 30:
                        player = Character('player', j * tile_size, i * tile_size, 5, 10)
                        hbar = Bar(10, 10, player.health, player.health)
                    elif tile == 31:
                        door = Exit(img, j * tile_size, i * tile_size)
                        exit_group.add(door)
                    elif tile == 32:
                        coin = Coin(img, j * tile_size, i * tile_size)
                        coin_group.add(coin)

        return player, hbar

    def draw(self):
        for tile in self.collision_tiles:
            # move tiles along with screen
            tile[1][0] += camera_scroll
            screen.blit(tile[0], tile[1])


class Blob(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = ((x + tile_size // 2), (y + (tile_size - self.image.get_height())))
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += camera_scroll
        blob_x = 0

    def walk(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


class Coin(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.transform.scale(img, (25, 25)).convert_alpha()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = ((x + tile_size // 2), (y + (tile_size - self.image.get_height())))

    def update(self):
        self.rect.x += camera_scroll


class Deco(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = ((x + tile_size // 2), (y + (tile_size - self.image.get_height())))

    def update(self):
        self.rect.x += camera_scroll


class Danger(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = ((x + tile_size // 2), (y + (tile_size - self.image.get_height())))

    def update(self):
        self.rect.x += camera_scroll


class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = ((x + tile_size // 2), (y + (tile_size - self.image.get_height())))

    def update(self):
        self.rect.x += camera_scroll


class Treasure(pygame.sprite.Sprite):
    def __init__(self, item, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item = item
        self.image = item_type[self.item]
        self.rect = self.image.get_rect()
        self.rect.midtop = ((x + tile_size // 2), (y + (tile_size - self.image.get_height())))

    def update(self):
        self.rect.x += camera_scroll


class Button:
    def __init__(self, x, y, image, scale):
        btn_width = image.get_width()
        btn_height = image.get_height()
        self.image = pygame.transform.scale(image, (int(btn_width * scale), int(btn_height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False

        # mouse position
        pos = pygame.mouse.get_pos()

        # check click
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

            elif pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action

shoot = False
restart_btn = Button(width // 2 - 150, height // 2 - 50, restart_img, 2)

ammo_group = pygame.sprite.Group()
treasure_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
bar_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
danger_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
tile_group = pygame.sprite.Group()

# level setup
level_layout = []
for row in range(rows):
    r = [-1] * columns
    level_layout.append(r)

with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    # individual row and tile, count
    for i, row in enumerate(reader):
        for j, tile in enumerate(row):
            level_layout[i][j] = int(tile)

world = Level()
player, hbar = world.game_data(level_layout)

def score_save():
    gscore = str(game_score)
    db = sqlite3.connect('score.db')
    db.execute("CREATE TABLE IF NOT EXISTS score(score TEXT)")
    cursor = db.cursor()
    cursor.execute("INSERT INTO score(score) VALUES (?)", (gscore,))
    db.commit()

def score_display():
    dscore = str(game_score)
    db = sqlite3.connect('score.db')
    cursor = db.cursor()
    cursor.execute("SELECT MAX(score) FROM score")
    data = cursor.fetchone()
    if data:
        draw_text('High Score:'+str(data[0]), font, 'white', 370,40)


running = True
keys = pygame.key.get_pressed()

while running:
    clock.tick(fps)

    draw_bg()
    # screen.blit(bg_img, (0, 0))
    # screen.blit(sun_img, (100, 100))
    screen.blit(coin_img, (10, 45))
    screen.blit(bullet_count, (11, 77))

    world.draw()
    player.update()
    player.draw()
    camera_scroll, level_complete = player.move(turn_left, turn_right)
    bg_scroll = camera_scroll
    if level_complete:
        level += 1
        bg_scroll = 0
        level_layout = restart()
        with open(f'level{level}_data.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            # individual row and tile, count
            for i, row in enumerate(reader):
                for j, tile in enumerate(row):
                    level_layout[i][j] = int(tile)

        world = Level()

        player, hbar = world.game_data(level_layout)

    if restart_btn.clicked is True:
        coin_score = 0
        score = 0
        restart_btn.clicked = False

    #   enemy.update()
    #   enemy.draw()
    #  enemy.enemy_movement()

    collided_coin = pygame.sprite.spritecollideany(player, coin_group)
    if collided_coin is not None:
        coin_audio.play()
        collided_coin.kill()
        coin_score += 1

    game_score = coin_score * 10

    collided_treasure = pygame.sprite.spritecollideany(player, treasure_group)
    if collided_treasure is not None and player.health < 90:
        collided_treasure.kill()
        player.health += 5

    elif collided_treasure is not None and player.bullet < 5:
        collided_treasure.kill()
        player.bullet += 3
        coin_audio.play()

    draw_text('x ' + str(coin_score), font, 'white', coin_img.get_width() + 25, 48)
    draw_text('Level:' + str(level), font, 'white', 700, 10)
    draw_text('x ' + str(player.bullet), font, 'white', coin_img.get_width() + 25, 79)
    draw_text('Score:' + str(game_score), font, 'white',370,10)

    for enemy in enemy_group:
        Blob.walk(enemy)

    if player.alive == False:
        restart_btn.draw(screen)
        score_save()

    hbar.draw(player.health)

    ammo_group.update()
    ammo_group.draw(screen)
    treasure_group.update()
    danger_group.update()
    decoration_group.update()
    exit_group.update()
    coin_group.update()

    enemy_group.draw(screen)
    enemy_group.update()
    treasure_group.draw(screen)
    coin_group.draw(screen)
    danger_group.draw(screen)
    decoration_group.draw(screen)
    exit_group.draw(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_LEFT:
                turn_left = True
                turn_right = False
            if event.key == pygame.K_RIGHT:
                turn_right = True
                turn_left = False

            if event.key == pygame.K_UP:
                player.jump = True

            if event.key == pygame.K_DOWN:
                player.jump = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                turn_left = False
            if event.key == pygame.K_RIGHT:
                turn_right = False
            if event.key == pygame.K_UP:
                player.jump = False
            if event.key == pygame.K_SPACE:
                shoot = False

        if player.alive:
            if shoot:
                player.shoot()
            if player.jumping:
                player.check_state(2)
            elif turn_left or turn_right:
                player.check_state(1)
            else:
                player.check_state(0)
        else:
            camera_scroll = 0
            if restart_btn.draw(screen):
                level_layout = restart()
                with open(f'level{level}_data.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    # individual row and tile, count
                    for i, row in enumerate(reader):
                        for j, tile in enumerate(row):
                            level_layout[i][j] = int(tile)

                world = Level()

                player, hbar = world.game_data(level_layout)
    score_display()
    pygame.display.update()
