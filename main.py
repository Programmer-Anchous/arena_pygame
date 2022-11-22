import sys

from tools import *
from weapon import *
from characters import *
from map import *


pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

WINDOW_SIZE = pygame.display.Info()
WINDOW_SIZE = (WINDOW_SIZE.current_w, WINDOW_SIZE.current_h)
FPS = 100

screen = pygame.display.set_mode(WINDOW_SIZE, pygame.FULLSCREEN)
display = pygame.Surface(WINDOW_SIZE)
clock = pygame.time.Clock()

true_scroll = [0, 0]

background = load_image("data/bg", scale=(2, 2))


map_ = Map(display, "data/map.txt")
player = Player(display, (200, 50), map_.get_rects())


# scrolling of the objects when player is moving
def parallax_scrolling() -> list:
    true_scroll[0] += (player.rect.x - true_scroll[0] - WINDOW_SIZE[0] // 2 + player.rect.width // 2) / 5
    true_scroll[1] += (player.rect.y - true_scroll[1] - WINDOW_SIZE[1] // 2 + player.rect.height // 2) / 5
    return [int(true_scroll[0]), int(true_scroll[1])]

clicked = False
running = True
while running:
    scroll = parallax_scrolling()

    display.fill((0, 0, 0))
    display.blit(background, (-scroll[0] * 0.1 - 400, -scroll[1] * 0.1 - 350))

    mx, my = pygame.mouse.get_pos()

    clicked = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            # player moving
            if event.key == pygame.K_a:
                player.moving_left = True
            if event.key == pygame.K_d:
                player.moving_right = True
            if event.key == pygame.K_SPACE:
                if player.air_timer < 6:
                    player.player_y_momentum = -12
            
            # hotkeys
            if event.key == pygame.K_ESCAPE:
                player.change_inventory()  # closing/opening inventory
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                player.moving_left = False
            if event.key == pygame.K_d:
                player.moving_right = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                clicked = True
                # player.fire(mx + scroll[0], my + scroll[1])
            
            if event.button == 4:
                player.scroll_inventory(1)
            if event.button == 5:
                player.scroll_inventory(-1)
    
    true_scroll = parallax_scrolling()
    map_.update(scroll)
    player.update(scroll, mx, my, clicked)

    screen.blit(display, (0, 0))
    pygame.display.update()
    clock.tick(FPS)