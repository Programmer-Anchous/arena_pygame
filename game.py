import sys
from time import sleep

from tools import *
from weapon import *
from characters import *
from map import *
from data.font.font import *


pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

WINDOW_SIZE = pygame.display.Info()
WINDOW_SIZE = (WINDOW_SIZE.current_w, WINDOW_SIZE.current_h)
FPS = 1000

screen = pygame.display.set_mode(WINDOW_SIZE, pygame.FULLSCREEN)
display = pygame.Surface(WINDOW_SIZE)
clock = pygame.time.Clock()

true_scroll = [0, 0]

# load images
background = load_image("data/images/bg", scale=(2, 2))

# load sounds
collide_button_sound = pygame.mixer.Sound("data/sounds/button.mp3")

tile_map = Map(display, "data/map.txt")
player = Player(display, (200, 50), tile_map.get_rects(), tile_map.get_platforms(), WINDOW_SIZE)

enemies = Enemies(display, tile_map.get_rects())


font2 = Font("data/font/letters.png", 2)
font3 = Font("data/font/letters.png", 3)

to_main_menu_image = font3.render("to main menu", (220, 220, 220))
to_main_menu_pressed_image = font3.render("to main menu", (255, 255, 0))
to_main_menu_button = Button(
    to_main_menu_image,
    to_main_menu_pressed_image,
    (WINDOW_SIZE[0] - 185, WINDOW_SIZE[1] - 30),
    display,
    collide_button_sound
)


def draw_fps():
    if player.inventory.is_opened:
        text = font2.render(f"fps {int(clock.get_fps())}", (220, 220, 220))
        display.blit(text, (WINDOW_SIZE[0] - 70, 5))


class Console:
    def __init__(self, display, font, enemies, player):
        self.letters = "abcdefghijklmnopqrstuvwxyz1234567890?!<>[]%-/"
        self.display = display
        self.font = font

        self.enemies = enemies
        self.player = player

        self.commands = {
            "/killall": self.enemies.kill_all,
            "/fullhp": self.player.full_hp
        }

        self.user_text = ""
        
        self.surf = pygame.Surface((400, 30))
        pygame.draw.rect(self.surf, (50, 60, 150), (0, 0, 400, 30), 0, 5)
        pygame.draw.rect(self.surf, (10, 20, 80), (0, 0, 400, 30), 2, 5)
        self.surf.set_colorkey((0, 0, 0))
        self.surf.set_alpha(240)

        description = [
            "</killall> - kills all enemies",
            "</fullhp> - fully restores your health",
        ]
        self.info = pygame.Surface((400, len(description) * 23 + 5))
        for i, line in enumerate(description, start=0):
            self.info.blit(font2.render(line, (220, 220, 220)), (10, i * 30))
        self.info.set_colorkey((0, 0, 0))


        self.is_opened = False

        self.back_space_pressed = False
        self.back_space_counter = 0
        self.back_space_delay = 8
        self.back_space_auto = 40

        self.history = ["", "/killall", "/fullhp"]
        self.index = 0
    
    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:  # CTRL+C
                    self.change()

                elif event.key == pygame.K_BACKSPACE:
                    self.back_space_pressed = True
                    self.back_space_counter = 0
                    # if command from history had been modified put it to current command
                    if self.history[self.index]:
                        self.history[self.index] = self.history[self.index][:-1]

                elif event.key == pygame.K_DOWN:
                    self.index -= 1
                elif event.key == pygame.K_UP:
                    self.index += 1
                
                elif self.is_opened:
                    if event.key == pygame.K_RETURN:
                        if self.history[self.index] in self.commands:
                            self.commands[self.history[self.index]]()
                            self.history[0] = self.history[self.index]
                            if len(self.history) > 1:
                                if self.history[0] == self.history[1]:  # don't log similar commands
                                    del self.history[0]
                            self.history.insert(0, "")  # log commands
                            if len(self.history) > 20:
                                del self.history[19:]
                        self.user_text = ""
                        self.index = 0
                    else:
                        letter = event.unicode
                        if letter in self.letters:
                            if len(self.user_text) < 39:
                                self.history[0] = self.history[self.index]
                                self.index = 0
                                self.history[self.index] += letter

                if self.index >= len(self.history):
                    self.index = len(self.history) - 1
                elif self.index < 0:
                    self.index = 0

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_BACKSPACE:
                    self.back_space_pressed = False
            
            self.user_text = self.history[self.index]

        if self.is_opened:
            if self.back_space_pressed:
                self.back_space_counter += 1
                if self.back_space_counter >= self.back_space_auto:
                    if self.history[self.index] and self.back_space_counter > self.back_space_delay:
                        self.back_space_counter -= self.back_space_delay
                        self.history[self.index] = self.history[self.index][:-1]
            
            self.display.blit(self.surf, (10, WINDOW_SIZE[1] - 40))
            if self.user_text:
                if self.user_text in self.commands:
                    color = (100, 190, 60)
                else:
                    color = (230, 230, 230)
                rendered_text = self.font.render(self.user_text, color)
                self.display.blit(rendered_text, (20, WINDOW_SIZE[1] - 32))
            
            self.user_text = self.history[self.index]
            self.display.blit(self.info, (20, WINDOW_SIZE[1] - self.info.get_height() - 60))
    
    def change(self):
        self.is_opened = not self.is_opened
        return self.is_opened


class Generator:
    def __init__(self, tile_map, player, enemies):
        self.tile_map = tile_map
        self.player = player
        self.enemies = enemies

        self.counter = 0
    
    def update(self, scroll):
        self.counter += 1
        if self.counter % 400 == 0:
            self.counter = 0
            self.enemies.add_enemy((random.randint(100, 500), random.randint(100, 400)), random.randint(500, 1900))


generator = Generator(tile_map, player, enemies)
console = Console(display,font2, enemies, player)


# scrolling of the objects when player is moving
def parallax_scrolling() -> list:
    true_scroll[0] += (player.rect.x - true_scroll[0] - WINDOW_SIZE[0] // 2 + player.rect.width // 2) / 5
    true_scroll[1] += (player.rect.y - true_scroll[1] - WINDOW_SIZE[1] // 2 + player.rect.height // 2) / 5
    return [int(true_scroll[0]), int(true_scroll[1])]


def main_game():
    clicked = False
    running = True
    while running:
        scroll = parallax_scrolling()

        display.fill((0, 0, 0))
        display.blit(background, (-scroll[0] * 0.1 - 400, -scroll[1] * 0.1 - 350))

        mx, my = pygame.mouse.get_pos()

        clicked = False
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicked = True
                    # player.fire(mx + scroll[0], my + scroll[1])
                
                if event.button == 4:
                    player.scroll_inventory(1)
                if event.button == 5:
                    player.scroll_inventory(-1)
            
            if not console.is_opened:
                if event.type == pygame.KEYDOWN:
                    # hotkeys
                    # if event.key == pygame.K_c:
                    #     console.change()
                        
                    if event.key == pygame.K_ESCAPE:
                        player.change_inventory()  # closing/opening inventory
                    
                    # player moving
                    if event.key == pygame.K_a:
                        player.moving_left = True
                    if event.key == pygame.K_d:
                        player.moving_right = True
                    if event.key == pygame.K_SPACE:
                        if player.air_timer < 6:
                            player.player_y_momentum = -12  # jumping
                    if event.key == pygame.K_s:
                        player.moving_down = True
                
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        player.moving_left = False
                    if event.key == pygame.K_d:
                        player.moving_right = False
                    if event.key == pygame.K_s:
                        player.moving_down = False
        
        tile_map.update(scroll)
        player.update(scroll, mx, my, clicked)

        enemies.update(scroll, player.bullets, player.arrows)

        generator.update(scroll)
        console.update(events)

        draw_fps()

        if player.inventory.is_opened:
            if to_main_menu_button.collided(mx, my):
                if clicked:
                    sleep(0.1)
                    break
            to_main_menu_button.update()

        screen.blit(display, (0, 0))
        pygame.display.update()
        clock.tick(FPS)

    player.stop()


if __name__ == "__main__":
    main_game()
