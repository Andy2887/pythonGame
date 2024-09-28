import pygame

pygame.init()

#game window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
LOWER_MARGIN = 100
SIDE_MARGIN = 300

clock = pygame.time.Clock()
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption('Level Editor')

ROWS = 16
MAX_COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS

# define game variables
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1

# loading background
pine1_image = pygame.image.load('assets/img/background/pine1.png').convert_alpha()
pine2_image = pygame.image.load('assets/img/background/pine2.png').convert_alpha()
sky_cloud_image = pygame.image.load('assets/img/background/sky_cloud.png').convert_alpha()
mountain_image = pygame.image.load('assets/img/background/mountain.png').convert_alpha()

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BABY_BLUE = (137, 207, 240)

# create function for drawing background
def draw_bg():
    screen.fill(BABY_BLUE)
    width = sky_cloud_image.get_width()
    for x in range(4):
        screen.blit(sky_cloud_image, ((x * width) -scroll * 0.5,0))
        screen.blit(mountain_image, ((x * width)-scroll * 0.6,SCREEN_HEIGHT - mountain_image.get_height() - 300))
        screen.blit(pine1_image, ((x * width)-scroll * 0.7, SCREEN_HEIGHT - pine1_image.get_height() - 150))
        screen.blit(pine2_image, ((x * width)-scroll * 0.8, SCREEN_HEIGHT - pine2_image.get_height()))

def draw_grid():
    # vertical lines
    for c in range(MAX_COLS + 1):
        pygame.draw.line(screen, WHITE, (c * TILE_SIZE - scroll, 0), (c * TILE_SIZE - scroll, SCREEN_HEIGHT))

    for c in range(ROWS + 1):
        pygame.draw.line(screen, WHITE, (0, c * TILE_SIZE), (SCREEN_WIDTH, c * TILE_SIZE))

run = True

while run:

    clock.tick(FPS)
    draw_bg()
    draw_grid()

    # scroll the map
    if scroll_left and scroll > 0:
        scroll -= 5 * scroll_speed
    if scroll_right:
        scroll += 5 * scroll_speed

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        # keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                scroll_left = True
            if event.key == pygame.K_d:
                scroll_right = True
            if event.key == pygame.K_LSHIFT:
                scroll_speed = 5

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                scroll_left = False
            if event.key == pygame.K_d:
                scroll_right = False
            if event.key == pygame.K_LSHIFT:
                scroll_speed = 1

    pygame.display.update()