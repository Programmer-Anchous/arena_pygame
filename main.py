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

arrows = Arrows(display, 10, 0.07)

background = load_image("data/bg", scale=(2, 2))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, display: pygame.Surface, start: tuple, end: tuple):
        self.display = display
        self.rect = pygame.Rect(500, 300, 70, 70)
        self.angle = 0

        self.dx = 0
        self.dy = 0
        self.speed = 15
    
    def update(self):
        self.angle += to_rad(4)
        self.angle %= math.pi * 2

        self.dx = int(self.speed * math.cos(self.angle))
        self.dy = int(self.speed * math.sin(self.angle))

        # print(math.hypot(self.dx, self.dy))

        self.rect.x += (self.dx)
        self.rect.y += (self.dy)

        pygame.draw.rect(self.display, (200, 200, 255), self.rect)


lightning = Lightning(display, WINDOW_SIZE)

map_ = Map(display, "data/map.txt")
player = Player(display, (200, 50), map_.get_rects())


def parallax_scrolling() -> list:
    true_scroll[0] += (player.rect.x - true_scroll[0] - WINDOW_SIZE[0] // 2 + player.rect.width // 2) / 5
    true_scroll[1] += (player.rect.y - true_scroll[1] - WINDOW_SIZE[1] // 2 + player.rect.height // 2) / 5
    return [int(true_scroll[0]), int(true_scroll[1])]


running = True
while running:
    scroll = parallax_scrolling()

    display.fill((0, 0, 0))
    display.blit(background, (-scroll[0] * 0.05 - 400, -scroll[1] * 0.05 - 350))

    mx, my = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                player.moving_left = True
            if event.key == pygame.K_d:
                player.moving_right = True
            if event.key == pygame.K_SPACE:
                if player.air_timer < 6:
                    player.player_y_momentum = -12
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                player.moving_left = False
            if event.key == pygame.K_d:
                player.moving_right = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # arrows.add_arrow(point1, (mx, my))
                pass
            if event.button == 3:
                lightning.new_lightning((200, 450), pygame.mouse.get_pos())
    
    true_scroll = parallax_scrolling()
    map_.update(scroll)
    player.update(scroll)
    
    arrows.update()

    lightning.update()

    screen.blit(display, (0, 0))
    pygame.display.update()
    clock.tick(FPS)