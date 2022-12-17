from tools import *
from weapon import *
from data.font.font import *


WEAPONS = [Gun, Bow]


def check_if_weapon(obj):
    for weap in WEAPONS:
        if isinstance(obj, weap):
            return True
    return False


class Inventory:
    def __init__(self, display, font):
        self.display = display
        self.items = [None] * 5 * 3
        self.is_opened = False

        self.cell_image = pygame.Surface((60, 60))
        pygame.draw.rect(self.cell_image, (70, 80, 170), (1, 1, 58, 58), 0, 10)
        pygame.draw.rect(self.cell_image, (10, 20, 80), (1, 1, 58, 58), 2, 10)
        self.cell_image.set_colorkey((0, 0, 0))
        self.cell_image.set_alpha(230)
        
        self.choosen_cell_image = pygame.Surface((60, 60))
        pygame.draw.rect(self.choosen_cell_image, (243, 198, 13), (0, 0, 60, 60), 0, 10)
        pygame.draw.rect(self.choosen_cell_image, (203, 158, 0), (0, 0, 60, 60), 2, 10)
        self.choosen_cell_image.set_colorkey((0, 0, 0))
        self.choosen_cell_image.set_alpha(240)


        self.cells = list()
        for i in range(3):
            for k in range(5):
                self.cells.append(pygame.Rect(k * 66 + 20, i * 66 + 30, 60, 60))
        
        self.current_item = 0

        self.draged = False
        self.draged_item = None

        self.font = font

        self.text_inventory = self.font.render(f"inventory", (240, 240, 240))
    
    def update(self):
        right_range = 5 * 3 if self.is_opened else 5
        for i in range(right_range):
            cell = self.cells[i]
            if i == int(self.current_item):
                self.display.blit(self.choosen_cell_image, (cell.topleft))
            else:
                self.display.blit(self.cell_image, (cell.topleft))

            if self.items[i] is not None:
                self.display.blit(self.items[i].icon, (cell.x + 10, cell.y + 10))
        
        if self.is_opened:
            self.display.blit(self.text_inventory, (22, 10))
    
    def scrolling(self, cells_scroll):
        self.current_item -= cells_scroll / 2

        if self.current_item > 4:
            self.current_item = 0
        elif self.current_item < 0:
            self.current_item = 4
    
    def add_item(self, item, pos=-1):
        if pos != -1:
            self.items[pos] = item
        elif None in self.items:
            index = self.items.index(None)
            self.items[index] = item
    
    def get_item(self, pos):
        item = self.items[pos]
        self.items[pos] = None
        return item
    
    def get_current_item(self):
        return self.items[int(self.current_item)]


class Entitiy(pygame.sprite.Sprite):
    def __init__(self, display):
        pygame.sprite.Sprite.__init__(self)
        self.display = display
        self.movement = [0, 0]
        self.animation_frames = {}
        self.animation_database = {}
        self.player_frame = 0
        self.moving_right = False
        self.moving_left = False
        self.moving_down = False
        self.player_flip = False
        self.player_y_momentum = 0
        self.air_timer = 0
        self.player_action = None
        self.player_image_id = None
        self.tile_rects = None
        self.collisions = {"top": False, "bottom": False, "right": False, "left": False}


# circular motion
class EnemyBeta(pygame.sprite.Sprite):
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


class Player(Entitiy):
    def __init__(self, display, coords, rects, platforms, WINDOW_SIZE):
        Entitiy.__init__(self, display)
        self.rects = rects
        self.platforms = platforms
        self.WINDOW_SIZE = WINDOW_SIZE

        self.animation_database['run'] = load_animation('data/animations/player/run', [6] * 6, self.animation_frames)
        self.animation_database['idle'] = load_animation('data/animations/player/idle', [15] * 4, self.animation_frames)
        self.image = self.animation_database['idle'][0]
        self.rect = self.animation_frames["idle_0"].get_rect(topleft=coords)

        self.item = None

        self.font = Font("data/font/letters.png", 2)

        self.inventory = Inventory(display, self.font)
        self.inventory.add_item(Gun(display))
        self.inventory.add_item(Bow(display))

        self.bullets = Bullets(display, 12)
        self.arrows = Arrows(display, 14, 0.15)

        self.moving_down_counter = 0
        self.real_moving_down = False  # for platforms
        self.moving_down_limit = 5

        self.float_health = 100
        self.health = self.float_health

        self.gravity = 1
        self.speed = 5

        self.bullet_sound = pygame.mixer.Sound("data/sounds/bullet1.mp3")
        self.bullet_sound.set_volume(0.1)

        self.arrow_sound = pygame.mixer.Sound("data/sounds/arrow.mp3")
        self.arrow_sound.set_volume(0.2)

        self.hurt_sounds = [
            pygame.mixer.Sound("data/sounds/hurt.mp3"),
            pygame.mixer.Sound("data/sounds/hurt1.mp3"),
            pygame.mixer.Sound("data/sounds/hurt2.mp3"),
            pygame.mixer.Sound("data/sounds/hurt3.mp3"),
            pygame.mixer.Sound("data/sounds/hurt4.mp3"),
        ]
        self.death_sound = pygame.mixer.Sound("data/sounds/death.mp3")
    
    def update(self, scroll, mx, my, clicked):
        self.float_health += 0.005
        if self.float_health > 100:
            self.float_health = 100
        
        self.health = int(self.float_health)
        self.move()

        # animations
        if pygame.mouse.get_pos()[0] < self.rect.center[0] - scroll[0]:
            self.player_flip = True
        else:
            self.player_flip = False

        if self.movement[0] == 0:
            self.player_action, self.player_frame = change_action(self.player_action, self.player_frame, 'idle')
        else:
            self.player_action, self.player_frame = change_action(self.player_action, self.player_frame, 'run')
            if self.movement[0] < 0:
                self.player_flip = True
            else:
                self.player_flip = False
        self.player_frame += 1
        if self.player_frame >= len(self.animation_database[self.player_action]):
            self.player_frame = 0
        self.player_image_id = self.animation_database[self.player_action][self.player_frame]
        self.image = self.animation_frames[self.player_image_id]

        self.display.blit(pygame.transform.flip(self.image, self.player_flip, False),
                     (self.rect.x - scroll[0], self.rect.y - scroll[1]))

        # self.display.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))

        self.update_item(scroll, mx, my, self)

        self.draw_healthbar()

        self.update_inventory()
        self.mouse_event(scroll, mx, my, clicked)

    def set_volume(self, num):
        self.bullet_sound.set_volume(num)
        self.arrow_sound.set_volume(num + 0.1)

    def fire(self, scroll, mx, my):
        mx += scroll[0]
        my += scroll[1]
        if check_if_weapon(self.item):
            if isinstance(self.item, Gun):
                self.bullets.add_bullet(self.rect.center, (mx, my))
                self.bullet_sound.play()
            elif isinstance(self.item, Bow):
                self.arrow_sound.play()
                self.arrows.add_arrow(self.rect.center, (mx, my))
    
    def update_item(self, scroll, mx, my, player):
        self.bullets.update(scroll, self.rects)
        self.arrows.update(scroll, self.rects)
        self.item = self.inventory.get_current_item()
        if self.item:
            self.item.update(scroll, mx, my, player)
    
    def mouse_event(self, scroll, mx, my, clicked):
        if clicked:
            if self.inventory.is_opened:
                for i in range(len(self.inventory.cells)):
                    if self.inventory.cells[i].collidepoint((mx, my)):
                        if self.inventory.draged:
                            if self.inventory.items[i] is None:
                                # if mouse collide one of the inventory cells and there -
                                # - is no item in this cell, we add drag_item to this cell
                                self.inventory.add_item(self.inventory.draged_item, i)
                                self.inventory.draged = False
                            else:
                                # if mouse collide one of the inventory cells and there -
                                # - is item in this cell, we switch this item to drag_item
                                # and drag_item to item in this cell
                                item = self.inventory.get_item(i)
                                self.inventory.add_item(self.inventory.draged_item, i)
                                self.inventory.draged_item = item
                            break
                        else:
                            # if there is item in the cell put it into the draged_item
                            item = self.inventory.get_item(i)
                            if item is not None:
                                self.inventory.draged_item = item
                                self.inventory.draged = True
                            break
                else:
                    # if the mouse does not collide with any of the
                    # inventory slots, the player starts using his item
                    self.fire(scroll, mx, my)
            else:
                # if inventory is closed you can choose your object by clicking on it
                for i in range(len(self.inventory.cells[:5])):
                    if self.inventory.cells[i].collidepoint((mx, my)):
                        self.inventory.current_item = i
                        break
                else:
                    self.fire(scroll, mx, my)
            
        if self.inventory.draged:
            icon = self.inventory.draged_item.icon
            self.display.blit(icon, (mx - icon.get_width() // 2 + 30, my - icon.get_height() // 2 + 30))
    
    def move(self):
        self.movement = [0, 0]
        if self.moving_right:
            self.movement[0] += self.speed
        if self.moving_left:
            self.movement[0] -= self.speed
        self.movement[1] += self.player_y_momentum
        self.player_y_momentum += self.gravity
        if self.player_y_momentum > 10:
            self.player_y_momentum = 10
        
        if self.real_moving_down:
            self.rect, self.collisions = move(self.rect, self.movement, self.rects)
        else:
            self.rect, self.collisions = move(self.rect, self.movement, self.rects + self.platforms)
        
        if self.moving_down == True:
            self.real_moving_down = True
            self.moving_down_counter = self.moving_down_limit
        
        self.moving_down_counter -= 1
        if self.moving_down_counter <= 0:
            self.real_moving_down = False
            self.moving_down_counter = 0


        if self.collisions["top"]:
            self.player_y_momentum = 0
        if self.collisions['bottom']:
            self.player_y_momentum = 0
            self.air_timer = 0
            self.is_jumping = False
        else:
            self.air_timer += 1

    def jump(self):
        if self.air_timer < 6:
            self.player_y_momentum = -20  # jumping
    
    def update_inventory(self):
        self.inventory.update()
    
    def change_inventory(self):
        self.inventory.is_opened = not self.inventory.is_opened

    def scroll_inventory(self, num):
        self.inventory.scrolling(num)

    def stop(self):
        self.moving_right = False
        self.moving_left = False
    
    def full_hp(self):
        self.float_health = 100
    
    def draw_healthbar(self):
        text = f"life  {self.health} / {100}"
        surf = self.font.render(text, (220, 220, 220))
        self.display.blit(surf, (self.WINDOW_SIZE[0] - 230, 10))

        pygame.draw.rect(  # lighter line backgrouns
            self.display,
            (70, 70, 70),
            (self.WINDOW_SIZE[0] - 280, 30, 250, 30),
            0,
            3)
        pygame.draw.rect(  # dark backgrouns
            self.display,
            (20, 20, 20),
            (self.WINDOW_SIZE[0] - 270, 38, 230, 14),
            0,
            3)

        pygame.draw.rect(  # red line
            self.display,
            (170, 20, 20),
            (self.WINDOW_SIZE[0] - 280, 30, 250 * (self.health / 100), 30),
            0,
            3)
        pygame.draw.rect(  # dark red line
            self.display,
            (140, 10, 10),
            (self.WINDOW_SIZE[0] - 280, 52, 250 * (self.health / 100), 8),
            0,
            3)
        pygame.draw.rect(  # light red line
            self.display,
            (200, 30, 30),
            (self.WINDOW_SIZE[0] - 280, 30, 250 * (self.health / 100), 8),
            0,
            3)

        pygame.draw.rect(  # border
            self.display,
            (30, 30, 30),
            (self.WINDOW_SIZE[0] - 280, 30, 250, 30),
            2,
            3)


class Enemy_Sniper(Entitiy):
    def __init__(self, display, coords, rects, platforms, targetx, targety, player):
        Entitiy.__init__(self, display)
        # these points are range of the way which enemy will walk
        self.moving_right = True
        self.point_A = targetx
        self.point_B = targety

        self.rects = rects
        self.platforms = platforms

        self.moving_down_counter = 0
        self.real_moving_down = False  # for platforms 

        self.animation_database['run'] = load_animation('data/animations/enemy/run', [7] * 6, self.animation_frames)
        self.animation_database['idle'] = load_animation('data/animations/enemy/idle', [18] * 4, self.animation_frames)
        self.image = self.animation_database['idle'][0]
        self.rect = self.animation_frames["idle_0"].get_rect(topleft=coords)

        self.current_item = Gun
        self.bullets = Bullets(self.display, 11)
        self.fire_counter = 0
        self.fire_limit = random.randrange(130, 170)

        self.health = 100

        self.player = player

        self.gravity = 1
        self.speed = random.randrange(3, 6)
        self.jump_force = 17
        self.is_jumping = False
        self.prev_is_jumping = False

        self.previous_coord = None

        self.distance = None

        self.gun = Gun(display)

        self.bullet_sound = pygame.mixer.Sound("data/sounds/bullet1.mp3")
        self.bullet_sound.set_volume(0.05)

    def update(self, scroll):
        self.distance = self.get_distance()
        if self.distance < 800:
            self.fire_counter += 1
            if self.fire_counter > self.fire_limit:
                self.fire_counter = 0
                self.fire(self.player.rect)

        self.move()
        self.update_bullets(scroll)

        # animations
        if self.movement[0] == 0:
            self.player_action, self.player_frame = change_action(self.player_action, self.player_frame, 'idle')
        else:
            self.player_action, self.player_frame = change_action(self.player_action, self.player_frame, 'run')
            if self.movement[0] < 0:
                self.player_flip = True
            else:
                self.player_flip = False
        self.player_frame += 1
        if self.player_frame >= len(self.animation_database[self.player_action]):
            self.player_frame = 0
        self.player_image_id = self.animation_database[self.player_action][self.player_frame]
        self.image = self.animation_frames[self.player_image_id]
        self.display.blit(pygame.transform.flip(self.image, self.player_flip, False),
                     (self.rect.x - scroll[0], self.rect.y - scroll[1]))
        
        # self.display.blit(pygame.transform.flip(self.image, self.player_flip, False),
        #              (self.rect.x - scroll[0], self.rect.y - scroll[1]))
        self.update_item(scroll)

        self.draw_health(scroll)

    def set_volume(self, num):
        self.bullet_sound.set_volume(num // 2)

    def update_item(self, scroll):
        if self.distance < 800:
            x, y = self.player.rect.x - scroll[0], self.player.rect.y - scroll[1] + 30
        else:
            if self.moving_right:
                x, y = self.rect.x - scroll[0] + 100, self.rect.y - scroll[1] + 30
            elif self.moving_left:
                x, y = self.rect.x - scroll[0] - 100, self.rect.y - scroll[1] + 30
        self.gun.update(scroll, x, y, self)

    def draw_health(self, scroll):
        green = int(self.health * 2.25)
        pygame.draw.rect(self.display, (255 - green, green, 0),
                         (self.rect.centerx - scroll[0] - 15, self.rect.y - scroll[1] - 15, 0.3 * self.health, 10))
        pygame.draw.rect(self.display, (0, 0, 0),
                         (self.rect.centerx - scroll[0] - 15, self.rect.y - scroll[1] - 15, 30, 10), 1)

    def move(self):
        self.movement = [0, 0]
        if self.moving_right:
            self.movement[0] += self.speed
        if self.moving_left:
            self.movement[0] -=self.speed
        self.movement[1] += self.player_y_momentum
        self.player_y_momentum += self.gravity
        if self.player_y_momentum > 10:
            self.player_y_momentum = 10
        
        if self.moving_down == True:
            self.real_moving_down = True
            self.moving_down_counter = 10
        
        self.moving_down_counter -= 1
        if self.moving_down_counter <= 0:
            self.real_moving_down = False
            self.moving_down_counter = 0
        
        # following the player if he is close to the enemy
        if self.distance < 500:
            if self.get_x_distance() > 200:
                if self.rect.x < self.player.rect.x:
                    self.moving_right = True
                    self.moving_left = False
                elif self.rect.x > self.player.rect.x:
                    self.moving_right = False
                    self.moving_left = True
        
        if self.rect.y > self.player.rect.y and chance(0.01):
            self.jump()
        
        # falling from platforms if player located lower then enemy
        if self.collisions["bottom"] and (self.player.rect.bottom - self.rect.bottom) > 30:
            self.moving_down = True
        else:
            self.moving_down = False

        # self.previous_coord = self.rect.x
        if self.real_moving_down:
            self.rect, self.collisions = move(self.rect, self.movement, self.rects)
        else:
            self.rect, self.collisions = move(self.rect, self.movement, self.rects + self.platforms)


        if self.collisions["top"]:
            self.player_y_momentum = 0
        if self.collisions['bottom']:
            self.jumps_count = 0
            self.prev_is_jumping = self.is_jumping
            self.is_jumping = False
            self.player_y_momentum = 0
            self.air_timer = 0
        else:
            self.air_timer += 1
        

        # bot moving algorithm
        if not self.is_jumping:
            if self.moving_right:
                if self.rect.x >= self.point_B or self.previous_coord == self.rect.x:
                    self.moving_right = False
                    self.moving_left = True
                    self.previous_coord = None
            elif self.moving_left:
                if self.rect.x <= self.point_A or self.previous_coord == self.rect.x:
                    self.moving_left = False
                    self.moving_right = True
                    self.previous_coord = None
        
        if self.collisions["bottom"]:
            self.previous_coord = None
        
        if self.collisions["right"] or self.collisions["left"]:
            self.jump()

    def jump(self):
        if self.air_timer < 6 and not self.is_jumping:
            self.previous_coord = self.rect.x
            self.player_y_momentum = -self.jump_force  # jumping
            self.prev_is_jumping = self.is_jumping
            self.is_jumping = True

    def update_bullets(self, scroll):
        self.bullets.update(scroll, self.rects)

    def fire(self, rect):
        self.bullet_sound.play()
        self.bullets.add_bullet((self.rect.x + 28, self.rect.y + 32), rect.center)
    
    def get_distance(self) -> int:
        return int(math.hypot(self.rect.x - self.player.rect.x, self.rect.y - self.player.rect.y))
    
    def get_x_distance(self) -> int:
        return abs(self.rect.x - self.player.rect.x)


class Enemies:
    def __init__(self, display, rects, platforms, player):
        self.display = display
        self.rects = rects
        self.platforms = platforms
        self.enemies = list()
        self.player = player

        self.bullets = Bullets(display, 11)

        self.hurt_sounds = [
            pygame.mixer.Sound("data/sounds/hurt.mp3"),
            pygame.mixer.Sound("data/sounds/hurt1.mp3"),
            pygame.mixer.Sound("data/sounds/hurt2.mp3"),
            pygame.mixer.Sound("data/sounds/hurt3.mp3"),
            pygame.mixer.Sound("data/sounds/hurt4.mp3"),
        ]
        for sound in self.hurt_sounds:
            sound.set_volume(0.2)
        self.death_sound = pygame.mixer.Sound("data/sounds/death.mp3")
        self.death_sound.set_volume(0.1)

        self.sound_pause = 50
        self.sound_counter = 0

        self.enemy_killed = False
    
    def kill_all(self):
        self.enemies.clear()
    
    def update(self, scroll, bullets, arrows):
        self.enemy_killed = False

        self.sound_counter -= 1
        if self.sound_counter < 0:
            self.sound_counter = 0
        
        i = 0
        while i < len(self.enemies):
            self.enemies[i].update(scroll)

            # check if player bullets collide with enemies
            k = 0
            while k < len(bullets.bullets):
                if bullets.bullets[k].get_hitbox().colliderect(self.enemies[i].rect):
                    self.enemies[i].health -= bullets.bullets[k].damage
                    del bullets.bullets[k]
                    if self.enemies[i].health <= 0:
                        self.enemy_killed = True
                        if chance(0.2):
                            self.sound_counter = self.sound_pause
                            self.death_sound.play()
                        
                        # if enemy died save his bullets
                        self.bullets.extend(self.enemies[i].bullets)
                        del self.enemies[i]
                        i -= 1
                        break
                    else:
                        if self.sound_counter == 0:
                            self.sound_counter = self.sound_pause
                            self.hurt_sounds[random.randrange(len(self.hurt_sounds))].play()
                    k -= 1
                k += 1
            
            # check if player arrows collide with enemies
            k = 0
            while k < len(arrows.arrows):
                if arrows.arrows[k].get_hitbox().colliderect(self.enemies[i].rect):
                    self.enemies[i].health -= arrows.arrows[k].damage
                    del arrows.arrows[k]
                    if self.enemies[i].health <= 0:
                        self.enemy_killed = True
                        if chance(0.2):
                            self.sound_counter = self.sound_pause
                            self.death_sound.play()
                        
                        # if enemy died save his bullets
                        self.bullets.extend(self.enemies[i].bullets)
                        del self.enemies[i]
                        i -= 1
                        break
                    else:
                        if self.sound_counter == 0:
                            self.sound_counter = self.sound_pause
                            self.hurt_sounds[random.randrange(len(self.hurt_sounds))].play()
                    k -= 1
                k += 1

            i += 1
        
        # check if enemies bullets or arrows collide with player
        for enemy in self.enemies:
            i = 0
            while i < len(enemy.bullets.bullets):
                if enemy.bullets.bullets[i].get_hitbox().colliderect(self.player):
                    del enemy.bullets.bullets[i]
                    self.player.float_health -= 5
                else:
                    i += 1
        
        # update bullets of died enemies
        self.bullets.update(scroll, self.rects)
        i = 0
        while i < len(self.bullets.bullets):
            if self.bullets.bullets[i].get_hitbox().colliderect(self.player):
                del self.bullets.bullets[i]
                self.player.float_health -= 5
            else:
                i += 1
    
    def set_volume(self, num):
        for sound in self.hurt_sounds:
            sound.set_volume(num + 0.1)
        self.death_sound.set_volume(num)
        for enemy in self.enemies:
            enemy.set_volume(num)

    def add_enemy(self, coords, targetx, targety):
        self.enemies.append(Enemy_Sniper(self.display, coords, self.rects, self.platforms, targetx, targety, self.player))
