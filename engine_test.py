from engine import *

from weapon import *
from characters import *
from map import *


images = [
    "data/images/bg1",
    "data/images/bg2",
    "data/images/bg3",
    "data/images/bg4",
    "data/images/bg5",
]


def load_bg(size=None):
    image = load_image(images[random.randrange(len(images))])
    if size:
        image = pygame.transform.scale(image, size)
    color = image.get_at((10, 10))
    light_force = sum(color[:3]) // 3
    light_force = min(255, light_force + 50)

    surf = pygame.Surface(image.get_size())
    surf.set_alpha(light_force)
    image.blit(surf, (0, 0))
    return image


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

        self.background_surf = pygame.Surface((self.info.get_width(), self.info.get_height() + 20))
        pygame.draw.rect(self.background_surf, (20, 20, 20), (0, 0, *self.background_surf.get_size()), 0, 5)
        pygame.draw.rect(self.background_surf, (40, 40, 40), (0, 0, *self.background_surf.get_size()), 2, 5)
        self.background_surf.set_alpha(200)
        self.background_surf.set_colorkey((0, 0, 0))

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
            coords = (20, self.WINDOW_SIZE[1] - self.info.get_height() - 60)
            self.display.blit(self.background_surf, (coords[0] - 10, coords[1] - 13))
            self.display.blit(
                self.info, coords
            )

    def change(self):
        self.is_opened = not self.is_opened
        return self.is_opened


class Generator:
    def __init__(self, tile_map, player, enemies):
        self.tile_map = tile_map
        self.player = player
        self.enemies = enemies

        self.length_x = self.tile_map.tile_width * self.tile_map.max_width - 200
        self.length_y = self.tile_map.tile_width * len(self.tile_map.data) - 200

        self.counter = 0
        self.spawn_time_max = 500
        self.spawn_time_min = 200
        self.spawn_time_limit = self.spawn_time_max
        self.acceleration = 0.1

    def update(self):
        self.counter += 1

        self.spawn_time_limit -= self.acceleration
        if self.spawn_time_limit < self.spawn_time_min:
            self.spawn_time_limit = self.spawn_time_min
        
        if self.counter > int(self.spawn_time_limit):
            self.counter = 0
            if len(self.enemies.enemies) < 50:
                self.enemies.add_enemy(
                    (random.randint(200, self.length_x), random.randint(200, self.length_y)),
                    random.randint(-500, -400),
                    random.randint(2100, 2200),
                )
            else:
                self.spawn_time_limit = self.spawn_time_max


class SettingsMenu(Loop):
    def user_init(self):
        self.collide_button_sound = pygame.mixer.Sound("data/sounds/button1.mp3")
        self.collide_button_sound.set_volume(0.2)

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
    def __init__(self, WINDOW_SIZE: tuple | None = None, FPS: int = 60, font_path: None | str = None, screen=None, map_path = "data/maps/map.txt"):
        self.tile_map_path = map_path
        super().__init__(WINDOW_SIZE, FPS, font_path, screen)

    def user_init(self):
        self.true_scroll = [0, 0]
        self.background = load_image("data/images/bg", scale=(2, 2))
        self.collide_button_sound = pygame.mixer.Sound("data/sounds/button1.mp3")
        self.collide_button_sound.set_volume(0.2)

        self.tile_map = Map(self.display, self.tile_map_path)
        self.player = Player(
            self.display,
            self.tile_map.player_spawn,
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

        self.settings_menu = SettingsMenu(None, 60, "data/font/letters.png", self.screen)
        self.previous_display = self.display.copy()

        self.score = 0
        self.speed = 1 / self.FPS

        self.kill_count = 0
    
    def update_score(self):
        self.score += self.speed
        text = self.font3.render(f"time {(int(self.score))}     kills {self.kill_count}", (220, 220, 220))
        self.display.blit(text, (self.WINDOW_SIZE[0] // 2 - text.get_width() // 2, 10))

    def user_events(self):
        scroll = self.parallax_scrolling()
        mx, my = pygame.mouse.get_pos()
        self.clicked = False

        # self.display.blit(self.background, (-scroll[0] * 0.1 - 400, -scroll[1] * 0.1 - 350))

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
        
        inventory_is_opened = self.player.inventory.is_opened
        if inventory_is_opened:
            if self.settings_menu_button.collided(mx, my):
                if self.clicked:
                    sleep(0.1)
                    self.settings_menu.set_background(self.previous_display)
                    self.settings_menu.run()
                    if self.settings_menu.get_status():
                        self.running = False
                    self.clicked = False

        self.tile_map.update(scroll)
        self.player.update(scroll, mx, my, self.clicked)

        self.enemies.update(scroll, self.player.bullets, self.player.arrows)
        if self.enemies.enemy_killed:
            self.kill_count += 1

        self.generator.update()
        self.console.update(self.events)

        self.draw_minimap()
        self.draw_fps()
        self.update_score()

        if inventory_is_opened:
            self.settings_menu_button.update()

        self.previous_display = self.display.copy()

        if self.player.health <= 0:
            self.running = False

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


class ChooseMapMenu(Loop):
    def user_init(self):
        self.collide_button_sound = pygame.mixer.Sound("data/sounds/button1.mp3")
        self.collide_button_sound.set_volume(0.2)

        self.bg_image = load_bg(self.WINDOW_SIZE)

        self.back_image = self.font5.render("back", (220, 220, 220))
        self.back_pressed_image = self.font5.render("back", (255, 255, 0))
        self.back_button = Button(self.back_image, self.back_pressed_image,
                            (self.WINDOW_SIZE[0] // 2 - self.back_image.get_width() // 2, self.WINDOW_SIZE[1] // 2 + 200),
                            self.display, self.collide_button_sound)
        
        self.classic_image = self.font5.render("classic", (220, 220, 220))
        self.classic_pressed_image = self.font5.render("classic", (255, 255, 0))
        self.classic_button = Button(self.classic_image, self.classic_pressed_image,
                            (self.WINDOW_SIZE[0] // 2 - self.classic_image.get_width() // 2 - 200, self.WINDOW_SIZE[1] // 2 - 110),
                            self.display, self.collide_button_sound)
        
        self.romb_image = self.font5.render("romb", (220, 220, 220))
        self.romb_pressed_image = self.font5.render("romb", (255, 255, 0))
        self.romb_button = Button(self.romb_image, self.romb_pressed_image,
                            (self.WINDOW_SIZE[0] // 2 - self.romb_image.get_width() // 2 - 200, self.WINDOW_SIZE[1] // 2 - 50),
                            self.display, self.collide_button_sound)
        
        self.labyrinth_image = self.font5.render("labyrinth", (220, 220, 220))
        self.labyrinth_pressed_image = self.font5.render("labyrinth", (255, 255, 0))
        self.labyrinth_button = Button(self.labyrinth_image, self.labyrinth_pressed_image,
                            (self.WINDOW_SIZE[0] // 2 - self.labyrinth_image.get_width() // 2 - 200, self.WINDOW_SIZE[1] // 2 + 10),
                            self.display, self.collide_button_sound)
        
        self.result_map = "classic"
        self.map_images = {
            "classic": Map.get_minimap_from_file("data/maps/map.txt"),
            "romb": Map.get_minimap_from_file("data/maps/map1.txt"),
            "labyrinth": Map.get_minimap_from_file("data/maps/map2.txt")
        }
        
    def user_events(self):
        mx, my = pygame.mouse.get_pos()
        self.clicked = False

        self.display.blit(self.bg_image, (0, 0))

        for event in self.get_events():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.clicked = True
        
        if self.back_button.collided(mx, my):
            if self.clicked:
                sleep(0.1)
                self.running = False
                return self.result_map
        
        if self.classic_button.collided(mx, my):
            if self.clicked:
                sleep(0.1)
                self.result_map = "classic"
        
        if self.romb_button.collided(mx, my):
            if self.clicked:
                sleep(0.1)
                self.result_map = "romb"
        
        if self.labyrinth_button.collided(mx, my):
            if self.clicked:
                sleep(0.1)
                self.result_map = "labyrinth"
        
        minimap = self.map_images[self.result_map]
        self.display.blit(minimap, (
            self.WINDOW_SIZE[0] // 2 - minimap.get_width() // 2 + 100,
            self.WINDOW_SIZE[1] // 2 - minimap.get_height() // 2 - 40
        ))
        
        self.classic_button.update()
        self.romb_button.update()
        self.back_button.update()
        self.labyrinth_button.update()


class MainMenu(Loop):
    def user_init(self):
        self.collide_button_sound = pygame.mixer.Sound("data/sounds/button1.mp3")
        self.collide_button_sound.set_volume(0.2)

        self.bg_image = load_bg(self.WINDOW_SIZE)
        

        # creating buttons
        self.exit_image = self.font5.render("exit", (220, 220, 220))
        self.exit_pressed_image = self.font5.render("exit", (255, 255, 0))
        self.exit_button = Button(self.exit_image, self.exit_pressed_image,
                            (self.WINDOW_SIZE[0] // 2 - self.exit_image.get_width() // 2, self.WINDOW_SIZE[1] // 2 + 100),
                            self.display, self.collide_button_sound)

        # self.back_image = self.font5.render("back", (220, 220, 220))
        # self.back_pressed_image = self.font5.render("back", (255, 255, 0))
        # self.back_button = Button(self.back_image, self.back_pressed_image,
        #                     (self.WINDOW_SIZE[0] // 2 - self.back_image.get_width() // 2, self.WINDOW_SIZE[1] // 2 + 160),
        #                     self.display, self.collide_button_sound)

        self.play_image = self.font5.render("play", (220, 220, 220))
        self.play_pressed_image = self.font5.render("play", (255, 255, 0))
        self.play_button = Button(self.play_image, self.play_pressed_image,
                            (self.WINDOW_SIZE[0] // 2 - self.play_image.get_width() // 2, self.WINDOW_SIZE[1] // 2 - 100),
                            self.display, self.collide_button_sound)
        
        self.choose_map_image = self.font5.render("choose map", (220, 220, 220))
        self.choose_map_pressed_image = self.font5.render("choose map", (255, 255, 0))
        self.choose_map_button = Button(self.choose_map_image, self.choose_map_pressed_image,
                            (self.WINDOW_SIZE[0] // 2 - self.choose_map_image.get_width() // 2, self.WINDOW_SIZE[1] // 2 + 0),
                            self.display, self.collide_button_sound)
        
        self.maps = {
            "classic": "data/maps/map.txt",
            "romb": "data/maps/map1.txt",
            "labyrinth": "data/maps/map2.txt"
        }
        self.current_map = "classic"
        
        # self.main_game = Game(None, 60, "data/font/letters.png", self.screen, "data/maps/map1.txt")
        self.choose_map_menu = ChooseMapMenu(None, 60, "data/font/letters.png", self.screen)

        self.clicked = False
    
    def user_events(self):
        mx, my = pygame.mouse.get_pos()
        self.clicked = False

        self.display.blit(self.bg_image, (0, 0))

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
                # self.main_game.run()

                # always start new game
                Game(None, 60, "data/font/letters.png", self.screen, self.maps[self.current_map]).run()
        
        if self.choose_map_button.collided(mx, my):
            if self.clicked:
                sleep(0.1)
                self.choose_map_menu.run()
                self.current_map = self.choose_map_menu.result_map

        self.play_button.update()
        self.exit_button.update()
        self.choose_map_button.update()


if __name__ == "__main__":
    # game = Game(None, 60, "data/font/letters.png")
    # game.run()
    main_ = MainMenu(None, 60, "data/font/letters.png")
    main_.run()
