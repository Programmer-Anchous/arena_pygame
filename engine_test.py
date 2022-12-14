from engine import *

from weapon import *
from characters import *
from map import *

from time import sleep


class Console:
    def __init__(self, display, font, enemies, player, WINDOW_SIZE):
        self.letters = "abcdefghijklmnopqrstuvwxyz1234567890?!<>[]%-/"
        self.display = display
        self.font = font
        self.WINDOW_SIZE = WINDOW_SIZE

        self.enemies = enemies
        self.player = player

        self.commands = {
            "/killall": self.enemies.kill_all,
            "/fullhp": self.player.full_hp,
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
            self.info.blit(self.font.render(line, (220, 220, 220)), (10, i * 30))
        self.info.set_colorkey((0, 0, 0))

        self.is_opened = False

        self.back_space_pressed = False
        self.back_space_counter = 0
        self.back_space_delay = 3
        self.back_space_auto = 30

        self.history = ["", "/killall", "/fullhp"]
        self.index = 0

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if (
                    event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL
                ):  # CTRL+C
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
                                if (
                                    self.history[0] == self.history[1]
                                ):  # don't log similar commands
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
                    if (
                        self.history[self.index]
                        and self.back_space_counter > self.back_space_delay
                    ):
                        self.back_space_counter -= self.back_space_delay
                        self.history[self.index] = self.history[self.index][:-1]

            self.display.blit(self.surf, (10, self.WINDOW_SIZE[1] - 40))
            if self.user_text:
                if self.user_text in self.commands:
                    color = (100, 190, 60)
                else:
                    color = (230, 230, 230)
                rendered_text = self.font.render(self.user_text, color)
                self.display.blit(rendered_text, (20, self.WINDOW_SIZE[1] - 32))

            self.user_text = self.history[self.index]
            self.display.blit(
                self.info, (20, self.WINDOW_SIZE[1] - self.info.get_height() - 60)
            )

    def change(self):
        self.is_opened = not self.is_opened
        return self.is_opened


class Generator:
    def __init__(self, tile_map, player, enemies):
        self.tile_map = tile_map
        self.player = player
        self.enemies = enemies

        self.counter = 290

    def update(self):
        self.counter += 1
        if self.counter % 300 == 0:
            self.counter = 0
            if len(self.enemies.enemies) < 1:
                self.enemies.add_enemy(
                    (random.randint(100, 200), random.randint(100, 110)),
                    random.randint(-500, -400),
                    random.randint(2100, 2200),
                )


class SettingsMenu(Loop):
    def user_init(self):
        self.collide_button_sound = pygame.mixer.Sound("data/sounds/button.mp3")

        self.to_main_menu_image = self.font4.render("to main menu", (220, 220, 220))
        self.to_main_menu_pressed_image = self.font4.render(
            "to main menu", (255, 255, 0)
        )
        self.to_main_menu_button = Button(
            self.to_main_menu_image,
            self.to_main_menu_pressed_image,
            (self.WINDOW_SIZE[0] // 2 - self.to_main_menu_image.get_width() // 2, 400),
            self.display,
            self.collide_button_sound,
        )

        self.continue_image = self.font4.render("continue", (220, 220, 220))
        self.continue_pressed_image = self.font4.render("continue", (255, 255, 0))
        self.continue_button = Button(
            self.continue_image,
            self.continue_pressed_image,
            (self.WINDOW_SIZE[0] // 2 - self.continue_image.get_width() // 2, 500),
            self.display,
            self.collide_button_sound,
        )

        self.background = None
        self.clicked = False

        self.closing = False
    
    def user_events(self):
        self.display.blit(self.background, (0, 0))

        self.alpha_surf = pygame.Surface(self.WINDOW_SIZE)
        self.alpha_surf.set_alpha(150)
        self.display.blit(self.alpha_surf, (0, 0))

        self.to_main_menu_button.update()
        self.continue_button.update()

        self.clicked = False
        
        mx, my = pygame.mouse.get_pos()

        for event in self.get_events():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.clicked = True
        
        if self.to_main_menu_button.collided(mx, my):
            if self.clicked:
                sleep(0.1)
                self.running = False
                self.closing = True
        
        if self.continue_button.collided(mx, my):
            if self.clicked:
                sleep(0.1)
                self.running = False
    
    def set_background(self, background: pygame.Surface) -> None:
        self.background = background
    
    def get_status(self) -> bool:
        status = self.closing
        self.closing = False
        return status


class Game(Loop):
    def user_init(self):
        self.true_scroll = [0, 0]
        self.background = load_image("data/images/bg", scale=(2, 2))
        self.collide_button_sound = pygame.mixer.Sound("data/sounds/button.mp3")

        self.tile_map = Map(self.display, "data/map.txt")
        self.player = Player(
            self.display,
            (200, 50),
            self.tile_map.get_rects(),
            self.tile_map.get_platforms(),
            self.WINDOW_SIZE,
        )
        self.enemies = Enemies(
            self.display,
            self.tile_map.get_rects(),
            self.tile_map.get_platforms(),
            self.player,
        )

        self.settings_menu_image = self.font3.render("settings", (220, 220, 220))
        self.settings_menu_pressed_image = self.font3.render(
            "settings", (255, 255, 0)
        )
        self.settings_menu_button = Button(
            self.settings_menu_image,
            self.settings_menu_pressed_image,
            (self.WINDOW_SIZE[0] - 130, self.WINDOW_SIZE[1] - 40),
            self.display,
            self.collide_button_sound,
        )

        self.generator = Generator(self.tile_map, self.player, self.enemies)
        self.console = Console(
            self.display, self.font2, self.enemies, self.player, self.WINDOW_SIZE
        )

        self.clicked = False

        self.mini_width = self.tile_map.mini_width

        self.settings_menu = SettingsMenu(None, 60, "data/font/letters.png")

        self.previous_display = self.display.copy()

    def user_events(self):
        scroll = self.parallax_scrolling()
        mx, my = pygame.mouse.get_pos()
        self.clicked = False

        for event in self.get_events():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.clicked = True

                if event.button == 4:
                    self.player.scroll_inventory(1)
                if event.button == 5:
                    self.player.scroll_inventory(-1)

            if not self.console.is_opened:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.player.change_inventory()  # closing/opening inventory

                    # player moving
                    if event.key == pygame.K_a:
                        self.player.moving_left = True
                    if event.key == pygame.K_d:
                        self.player.moving_right = True
                    if event.key == pygame.K_SPACE:
                        self.player.jump()
                    if event.key == pygame.K_s:
                        self.player.moving_down = True

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.player.moving_left = False
                    if event.key == pygame.K_d:
                        self.player.moving_right = False
                    if event.key == pygame.K_s:
                        self.player.moving_down = False
        
        if self.player.inventory.is_opened:
            if self.settings_menu_button.collided(mx, my):
                if self.clicked:
                    sleep(0.1)
                    self.settings_menu.set_background(self.previous_display)
                    self.settings_menu.run()
                    if self.settings_menu.get_status():
                        self.running = False
                    self.clicked = False

            self.settings_menu_button.update()

        self.tile_map.update(scroll)
        self.player.update(scroll, mx, my, self.clicked)

        self.enemies.update(scroll, self.player.bullets, self.player.arrows)

        self.generator.update()
        self.console.update(self.events)

        self.draw_minimap()

        self.draw_fps()

        self.previous_display = self.display.copy()
        

    def draw_minimap(self):
        minimap = self.tile_map.get_minimap().copy()
        for enemy in self.enemies.enemies:
            pygame.draw.rect(
                minimap,
                (255, 70, 70),
                (
                    enemy.rect.x / 30 * self.mini_width + 5,
                    enemy.rect.y / 30 * self.mini_width + 5,
                    self.mini_width,
                    self.mini_width * 1.8,
                ),
            )
        
        pygame.draw.rect(
            minimap,
            (10, 250, 10),
            (
                self.player.rect.x / 30 * self.mini_width + 5,
                self.player.rect.y / 30 * self.mini_width + 5,
                self.mini_width,
                self.mini_width * 1.8,
            ),
        )

        text = self.font2.render("minimap", (220, 220, 220))
        self.display.blit(text, (self.WINDOW_SIZE[0] - minimap.get_width() - 300, 10))
        self.display.blit(
            minimap, (self.WINDOW_SIZE[0] - minimap.get_width() - 310, 30)
        )

    def user_end_action(self):
        self.player.stop()

    def draw_fps(self):
        if self.player.inventory.is_opened:
            text = self.font2.render(
                f"fps {int(self.clock.get_fps())}", (220, 220, 220)
            )
            self.display.blit(text, (self.WINDOW_SIZE[0] - 70, 5))

    def parallax_scrolling(self) -> list:
        self.true_scroll[0] += (
            self.player.rect.x
            - self.true_scroll[0]
            - self.WINDOW_SIZE[0] // 2
            + self.player.rect.width // 2
        ) / 5
        self.true_scroll[1] += (
            self.player.rect.y
            - self.true_scroll[1]
            - self.WINDOW_SIZE[1] // 2
            + self.player.rect.height // 2
        ) / 5
        return [int(self.true_scroll[0]), int(self.true_scroll[1])]


class MainMenu(Loop):
    def user_init(self):
        self.collide_button_sound = pygame.mixer.Sound("data/sounds/button.mp3")

        # creating buttons
        self.exit_image = self.font5.render("exit", (220, 220, 220))
        self.exit_pressed_image = self.font5.render("exit", (255, 255, 0))
        self.exit_button = Button(self.exit_image, self.exit_pressed_image,
                            (self.WINDOW_SIZE[0] // 2 - self.exit_image.get_width() // 2, self.WINDOW_SIZE[1] // 2 + 160),
                            self.display, self.collide_button_sound)

        self.back_image = self.font5.render("back", (220, 220, 220))
        self.back_pressed_image = self.font5.render("back", (255, 255, 0))
        self.back_button = Button(self.back_image, self.back_pressed_image,
                            (self.WINDOW_SIZE[0] // 2 - self.back_image.get_width() // 2, self.WINDOW_SIZE[1] // 2 + 160),
                            self.display, self.collide_button_sound)

        self.play_image = self.font5.render("play", (220, 220, 220))
        self.play_pressed_image = self.font5.render("play", (255, 255, 0))
        self.play_button = Button(self.play_image, self.play_pressed_image,
                            (self.WINDOW_SIZE[0] // 2 - self.back_image.get_width() // 2, self.WINDOW_SIZE[1] // 2 + 60),
                            self.display, self.collide_button_sound)
        
        self.main_game = Game(None, 60, "data/font/letters.png")

        self.clicked = False
    
    def user_events(self):
        mx, my = pygame.mouse.get_pos()
        self.clicked = False

        text = self.font3.render(f"fps {int(self.clock.get_fps())}", (255, 255, 255))
        for event in self.get_events():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicked = True

        if self.exit_button.collided(mx, my):
            if self.clicked:
                sleep(0.1)
                self.running = False

        if self.play_button.collided(mx, my):
            if self.clicked:
                sleep(0.1)
                self.main_game.run()

        self.display.blit(text, (10, 10))

        self.play_button.update()
        self.exit_button.update()



if __name__ == "__main__":
    # game = Game(None, 60, "data/font/letters.png")
    # game.run()
    main_ = MainMenu(None, 60, "data/font/letters.png")
    main_.run()
