import pygame
import sys
import random
import csv

# Initialize Pygame
pygame.init()

# set framerate
clock = pygame.time.Clock()
FPS = 60


# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

# Define game variables
ROWS = 16
COLS = 150
GRAVITY = 0.95
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
difficulty = "Normal"
level = 1
SCROLL_THRESH = 200
screen_scroll = 0
bg_scroll = 0



# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BABY_BLUE = (137, 207, 240)


# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# assets loading
BG = pygame.image.load("assets/menu_options/Background.jpg")
BG_2 = pygame.image.load("assets/menu_options/Background_2.jpg")
RECT_IMAGE = pygame.image.load("assets/menu_options/grey_rect.png")
bullet_img = pygame.image.load('assets/img/icons/bullet.png').convert_alpha()
grenade_img = pygame.image.load('assets/img/icons/grenade.png').convert_alpha()
heal_box_img = pygame.image.load('assets/img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('assets/img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('assets/img/icons/grenade_box.png').convert_alpha()

# loading background
pine1_image = pygame.image.load('assets/img/background/pine1.png').convert_alpha()
pine2_image = pygame.image.load('assets/img/background/pine2.png').convert_alpha()
sky_cloud_image = pygame.image.load('assets/img/background/sky_cloud.png').convert_alpha()
mountain_image = pygame.image.load('assets/img/background/mountain.png').convert_alpha()

# store tiles in a list
tile_img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'assets/img/tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    tile_img_list.append(img)

item_boxes = {
    'Health': heal_box_img,
    'Ammo' : ammo_box_img,
    'Grenade' : grenade_box_img
}

# initialize sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# draw background
def draw_bg():
    width = sky_cloud_image.get_width()
    for x in range(5):
        screen.blit(sky_cloud_image, (x * width - bg_scroll * 0.5, 0))
        screen.blit(mountain_image, (x * width - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_image.get_height() - 300))
        screen.blit(pine1_image, (x * width - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_image.get_height() - 150))
        screen.blit(pine2_image, (x * width - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_image.get_height()))

def draw_text(text, text_col, x, y):
    font = get_font(30)
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))

# Button Class
class Button():
    def __init__(self, image, pos, text_input, font, base_color, hover_color):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.text_input = text_input
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self,screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self,position):
        if position[0] in range(self.rect.left,self.rect.right) and position[1] in range(self.rect.top,self.rect.bottom):
            return True
        return False

    def changeColor(self,position):
        if position[0] in range(self.rect.left,self.rect.right) and position[1] in range(self.rect.top,self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hover_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)

# soldier class
class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, num_grenades):
        pygame.sprite.Sprite.__init__(self)
        # basic parameters for soldier
        self.alive = True
        self.char_type = char_type
        self.scale = scale
        self.speed = speed

        # moving variables for soldier
        self.moving_left = False
        self.moving_right = False
        self.direction = 1

        # variables related to jump
        self.flip = False
        self.jump = False
        self.in_air = False
        self.vel_y = 0

        # variables related to combat
        self.ammo = ammo
        self.start_ammo = ammo
        self.is_shooting = False
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.num_grenades = num_grenades
        self.grenade = False
        self.grenade_thrown = False

        # variables related to AI characters
        self.move_counter = 0
        self.idling = False
        self.idling_counter = 100
        self.vision = pygame.Rect(0, 0, 150, 20)


        # create an animation list
        # Note:
        # action 0 is Idle
        # action 1 is Run
        # action 2 is Jump
        # action 3 is Death

        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        temp_list = []

        # Keep track of time
        self.update_time = pygame.time.get_ticks()

        # load idle images for soldier
        for i in range(5):
            # load soldier image
            img = pygame.image.load(f'assets/img/{self.char_type}/Idle/{i}.png').convert_alpha()
            # get the original size of the image
            width, height = img.get_size()
            # scale the image based on the scale factor
            img = pygame.transform.scale(img, (int(width * scale), int(height * scale)))
            # store the image into the temp list
            temp_list.append(img)
        # append the temp list to the animation list
        self.animation_list.append(temp_list)
        temp_list = []

        # load run images for soldier
        for i in range(6):
            # load soldier image
            img = pygame.image.load(f'assets/img/{self.char_type}/Run/{i}.png').convert_alpha()
            # get the original size of the image
            width, height = img.get_size()
            # scale the image based on the scale factor
            img = pygame.transform.scale(img, (int(width * scale), int(height * scale)))
            # store the image into the temp list
            temp_list.append(img)
        # append the temp list to the animation list
        self.animation_list.append(temp_list)
        temp_list = []

        # load jump images for soldier
        for i in range(1):
            # Load soldier image
            img = pygame.image.load(f'assets/img/{self.char_type}/Jump/{i}.png').convert_alpha()
            # Get the original size of the image
            width, height = img.get_size()
            # Scale the image based on the scale factor
            img = pygame.transform.scale(img, (int(width * scale), int(height * scale)))
            # Store the image into the temp list
            temp_list.append(img)
        # append the temp list to the animation list
        self.animation_list.append(temp_list)
        temp_list = []

        # load death images for soldier
        for i in range(8):
            # Load soldier image
            img = pygame.image.load(f'assets/img/{self.char_type}/Death/{i}.png').convert_alpha()
            # Get the original size of the image
            width, height = img.get_size()
            # Scale the image based on the scale factor
            img = pygame.transform.scale(img, (int(width * scale), int(height * scale)))
            # Store the image into the temp list
            temp_list.append(img)
            # Append the temp list to the animation list
        self.animation_list.append(temp_list)
        temp_list = []

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

    # this method settles the variables related to moving, such as self.action, position, etc
    def move(self, world):

        screen_scroll = 0

        # reset movement variables
        dx = 0
        dy = 0

        if self.alive:
            # assign moving variables
            if self.jump and not self.in_air:
                self.vel_y = -18
                self.jump = False
                self.in_air = True
            elif self.moving_left:
                dx = -self.speed
                self.flip = True
                self.direction = -1
            elif self.moving_right:
                dx = self.speed
                self.flip = False
                self.direction = 1

            # update character action
            if self.in_air:
                self.update_action(2)
            elif self.moving_left or self.moving_right:
                self.update_action(1)
            else:
                self.update_action(0)

        # apply gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        # check collision
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                dx = 0
                # if the ai hits the wall, make it turn around
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                # check if below the ground, i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above ground
                else:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # check if going off the screen
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        # update rect position
        self.rect.x += dx
        self.rect.y += dy

        # update scroll
        if self.char_type == 'player':
            if ((self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)
                    or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx))):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll

    # this method takes the self.action and update the animation pattern accordingly
    def update_animation(self):

        # update animation
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]

        # check if enough time has passed since last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            if self.frame_index >= len(self.animation_list[self.action]):
                if self.action == 3:
                    self.frame_index = len(self.animation_list[self.action]) - 1
                else:
                    self.frame_index = 0

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()


    def shoot(self):
        if self.is_shooting and self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 10
            bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction),
                            self.rect.centery, self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1
        elif self.grenade and not self.grenade_thrown and self.num_grenades > 0:
            grenade = Grenade(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction),
                              self.rect.top, self.direction)
            grenade_group.add(grenade)
            self.grenade_thrown = True
            self.num_grenades -= 1

    # a general method that updates everything for the soldier

    def ai(self):
        if self.alive and player.alive:
            if not self.idling and random.randint(1,100) == 5:
                self.idling = True
                self.moving_right = False
                self.moving_left = False

            # check if the ai is near the player
            if self.vision.colliderect(player.rect):
                # stop running and face player
                self.idling = True
                self.moving_right = False
                self.moving_left = False
                self.is_shooting = True

            # if no player is in sight, continue to patrol
            else:
                self.is_shooting = False
                if self.idling:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False  # stop idling after the counter
                        self.idling_counter = 100

                else:
                    if self.direction == 1:
                        self.moving_right = True
                    else:
                        self.moving_right = False

                    self.moving_left = not self.moving_right
                    self.move_counter += 1

                # update AI vision
                self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                if self.move_counter > TILE_SIZE * 2:
                    self.direction *= -1
                    self.moving_right = not self.moving_right
                    self.moving_left = not self.moving_left
                    self.move_counter = 0
        else:
            self.is_shooting = False

        # scroll
        self.rect.x += screen_scroll

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def update(self, world):
        # update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        self.update_animation()
        self.draw()
        screen_scroll = self.move(world)
        self.shoot()
        self.check_alive()
        return screen_scroll

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # update with new health
        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

# initialize soldier object for player
player = Soldier('player', 0, 0, 1.8, 2, 20, 5)
health_bar = HealthBar(10, 10, player.health, player.health)


class World():

    def __init__(self):
        self.obstacle_list = []
    def process_data(self, data):
        self.level_length = len(data[0])
        # iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                # ignore blank tiles
                if tile >= 0:
                    img = tile_img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif 9 <= tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif 11 <= tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:
                        global player, health_bar
                        # initialize soldier object for player
                        player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 1.8, 4, 20, 5)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:
                        # create enemy
                        enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.8, 4, 20, 0)
                        enemy_group.add(enemy)
                    elif tile == 17:
                        # create ammo box
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18:
                        # create grenade box
                        item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19:
                        # create health box
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20:
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):

    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll
        if pygame.sprite.collide_rect(self, player):
            # check what kind of box it was
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.num_grenades += 3
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction

    def update(self, world):
        # move the bullet
        self.rect.x += (self.direction * self.speed)
        self.rect.x += screen_scroll

        # check if the bullet is outside screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        # check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()

        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()



class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 12
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction

    def update(self, world):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        # check for collision with level
        for tile in world.obstacle_list:

            # check for collision with walls
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                self.direction *= -1
                dx = self.direction * self.speed

            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                self.speed = 0
                # check if below the ground, i.e. throwing up
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check if falling
                else:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom


        # update grenade position
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        # countdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 1)
            explosion_group.add(explosion)
            # do damage to character based on scale
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and abs(
                    self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 40
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE and abs(
                    self.rect.centery - player.rect.centery) < TILE_SIZE:
                player.health -= 90

            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and abs(
                        self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 40
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE and abs(
                        self.rect.centery - enemy.rect.centery) < TILE_SIZE:
                    enemy.health -= 90



class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for i in range(1,6):
            img = pygame.image.load(f'assets/img/explosion/exp{i}.png').convert_alpha()
            width, height = img.get_size()
            img = pygame.transform.scale(img, (int(width * scale), int(height * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.counter = 0

    def update(self):
        EXPLOSION_SPEED = 4
        self.rect.x += screen_scroll
        # update explosion animation
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            # if the animation is complete, delete explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]





def get_font(size):
    return pygame.font.Font("assets/menu_options/font.ttf", size)


# welcome screen
def welcome_screen():
    pygame.display.set_caption("Welcome Screen")

    while True:
        screen.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(30).render("DON'T BUMP YOUR HEAD", True, BLACK)
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 125))

        #initialize buttons
        PLAY_BUTTON = Button(image=RECT_IMAGE, pos=(640, 300),
                             text_input="PLAY", font=get_font(30), base_color="#d7fcd4", hover_color="White")
        OPTIONS_BUTTON = Button(image=RECT_IMAGE, pos=(640, 450),
                                text_input="OPTIONS", font=get_font(30), base_color="#d7fcd4", hover_color="White")
        QUIT_BUTTON = Button(image=RECT_IMAGE, pos=(640, 600),
                             text_input="QUIT", font=get_font(30), base_color="#d7fcd4", hover_color="White")

        screen.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()



# options screen
def options():
    global difficulty
    pygame.display.set_caption("Options Screen")
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        screen.blit(BG_2, (0, 0))

        OPTIONS_TEXT = get_font(45).render("Please choose difficulty.", True, "White")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5))
        screen.blit(OPTIONS_TEXT, OPTIONS_RECT)

        OPTIONS_BACK = Button(image=RECT_IMAGE, pos=(SCREEN_WIDTH // 2, 600),
                              text_input="BACK", font=get_font(30), base_color="Black", hover_color=WHITE)

        OPTIONS_EASY = Button(image=RECT_IMAGE, pos=(SCREEN_WIDTH // 2, 275),
                              text_input="EASY", font=get_font(40), base_color=GREEN, hover_color=WHITE)

        OPTIONS_NORMAL = Button(image=RECT_IMAGE, pos=(SCREEN_WIDTH // 2, 375),
                              text_input="NORMAL", font=get_font(40), base_color=BABY_BLUE, hover_color=WHITE)

        OPTIONS_HARD = Button(image=RECT_IMAGE, pos=(SCREEN_WIDTH // 2, 475),
                              text_input="HARD", font=get_font(40), base_color=RED, hover_color=WHITE)

        for button in [OPTIONS_BACK, OPTIONS_EASY, OPTIONS_NORMAL, OPTIONS_HARD]:
            button.changeColor(OPTIONS_MOUSE_POS)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    welcome_screen()
                if OPTIONS_EASY.checkForInput(OPTIONS_MOUSE_POS):
                    difficulty = "Easy"
                    difficulty_set_screen()
                if OPTIONS_NORMAL.checkForInput(OPTIONS_MOUSE_POS):
                    difficulty = "Normal"
                    difficulty_set_screen()
                if OPTIONS_HARD.checkForInput(OPTIONS_MOUSE_POS):
                    difficulty = "Hard"
                    difficulty_set_screen()

        pygame.display.update()

def difficulty_set_screen():
    while True:
        DIFFICULTY_SET_MOUSE_POS = pygame.mouse.get_pos()

        screen.blit(BG_2, (0, 0))

        # render the first line
        line1 = "Your difficulty is set to:"
        DIFFICULTY_SET_TEXT_1 = get_font(40).render(line1, True, "White")
        DIFFICULTY_SET_RECT_1 = DIFFICULTY_SET_TEXT_1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))

        # set Difficulty Color
        if (difficulty == "Easy"):
            DIFFICULTY_COLOR = GREEN
        elif (difficulty == "Normal"):
            DIFFICULTY_COLOR = BABY_BLUE
        else:
            DIFFICULTY_COLOR = RED

        # render the second line (DIFFICULTY)
        DIFFICULTY_SET_TEXT_2 = get_font(40).render(difficulty, True, DIFFICULTY_COLOR)
        DIFFICULTY_SET_RECT_2 = DIFFICULTY_SET_TEXT_2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 100))

        # blit both lines to the screen
        screen.blit(DIFFICULTY_SET_TEXT_1, DIFFICULTY_SET_RECT_1)
        screen.blit(DIFFICULTY_SET_TEXT_2, DIFFICULTY_SET_RECT_2)

        DIFFICULTY_SET_BACK = Button(image=None, pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.25 - 50),
                              text_input="BACK", font=get_font(40), base_color="Black", hover_color="Yellow")

        DIFFICULTY_SET_BACK.changeColor(DIFFICULTY_SET_MOUSE_POS)
        DIFFICULTY_SET_BACK.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if DIFFICULTY_SET_BACK.checkForInput(DIFFICULTY_SET_MOUSE_POS):
                    welcome_screen()

        pygame.display.update()




# game screen
def play():

    pygame.display.set_caption('shooter')


    # create empty tile list
    world_data = []
    for row in range(ROWS):
        r = [-1] * COLS
        world_data.append(r)

    # load in level data and create world
    with open(f'assets/level{level}_data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for x, row in enumerate(reader):
            for y, tile in enumerate(row):
                world_data[x][y] = int(tile)

    world = World()
    world.process_data(world_data)


    while True:

        clock.tick(FPS)
        draw_bg()
        world.draw()
        global screen_scroll, bg_scroll
        screen_scroll = player.update(world)
        bg_scroll -= screen_scroll

        for enemy in enemy_group:
            enemy.update(world)
            enemy.ai()

        # show relevant stats
        draw_text(f'AMMO: ', BLACK, 10, 35)
        for x in range(player.ammo):
            screen.blit(bullet_img, (160 + (x * 10), 40))
        draw_text(f'GRENADES: ', BLACK, 10, 70)
        for x in range(player.num_grenades):
            screen.blit(grenade_img, (300 + (x * 15), 75))
        health_bar.draw(player.health)

        # update and draw groups
        bullet_group.update(world)
        grenade_group.update(world)
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()

        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)



        for event in pygame.event.get():
            # quit game
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # keyboard presses
            if event.type == pygame.KEYDOWN:

                # player movement
                if event.key == pygame.K_a:
                    player.moving_left = True
                if event.key == pygame.K_d:
                    player.moving_right = True
                if event.key == pygame.K_w:
                    player.jump = True
                if event.key == pygame.K_SPACE:
                    player.is_shooting = True
                if event.key == pygame.K_g:
                    player.grenade = True

            # keyboard button released
            if event.type == pygame.KEYUP:

                # player movement
                if event.key == pygame.K_a:
                    player.moving_left = False
                if event.key == pygame.K_d:
                    player.moving_right = False
                if event.key == pygame.K_SPACE:
                    player.is_shooting = False
                if event.key == pygame.K_g:
                    player.grenade = False
                    player.grenade_thrown = False

        pygame.display.update()

welcome_screen()


