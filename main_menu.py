import sys

from tools import *
from data.font.font import *
from game import main_game
from time import sleep


pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
monitor = (pygame.display.Info().current_w, pygame.display.Info().current_h)
WINDOW_SIZE = monitor
screen = pygame.display.set_mode(monitor, pygame.FULLSCREEN)
display = pygame.Surface(monitor)
clock = pygame.time.Clock()
FPS = 60

font_3 = Font("data/font/letters.png", 3)
font_4 = Font("data/font/letters.png", 4)
font_5 = Font("data/font/letters.png", 5)

collide_button_sound = pygame.mixer.Sound("data/sounds/button.mp3")

# creating buttons
exit_image = font_5.render("exit", (220, 220, 220))
exit_pressed_image = font_5.render("exit", (255, 255, 0))
exit_button = Button(exit_image, exit_pressed_image,
                     (WINDOW_SIZE[0] // 2 - exit_image.get_width() // 2, WINDOW_SIZE[1] // 2 + 160),
                     display, collide_button_sound)

back_image = font_5.render("back", (220, 220, 220))
back_pressed_image = font_5.render("back", (255, 255, 0))
back_button = Button(back_image, back_pressed_image,
                     (WINDOW_SIZE[0] // 2 - back_image.get_width() // 2, WINDOW_SIZE[1] // 2 + 160),
                     display, collide_button_sound)

play_image = font_5.render("play", (220, 220, 220))
play_pressed_image = font_5.render("play", (255, 255, 0))
play_button = Button(play_image, play_pressed_image,
                     (WINDOW_SIZE[0] // 2 - back_image.get_width() // 2, WINDOW_SIZE[1] // 2 + 60),
                     display, collide_button_sound)

running = True
while running:
    display.fill((40, 40, 40))
    mx, my = pygame.mouse.get_pos()
    click = False

    text = font_3.render(f"fps {int(clock.get_fps())}", (255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                click = True

    if exit_button.collided(mx, my):
        if click:
            sleep(0.1)
            break

    if play_button.collided(mx, my):
        if click:
            sleep(0.1)
            main_game()

    display.blit(text, (10, 10))

    play_button.update()
    exit_button.update()
    screen.blit(display, (0, 0))
    pygame.display.update()
    clock.tick(FPS)