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
    def __init__(self, display):
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

        font = Font("data/font/letters.png", 2)

        self.text_inventory = font.render(f"inventory", (240, 240, 240))
    
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
        self.collisions = None


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


class Player(pygame.sprite.Sprite):
    def __init__(self, display, coords, rects, platforms, WINDOW_SIZE):
        Entitiy.__init__(self, display)
        self.rects = rects
        self.platforms = platforms
        self.WINDOW_SIZE = WINDOW_SIZE
        self.image = pygame.Surface((30, 50))
        self.image.fill((10, 20, 200))
        pygame.draw.rect(self.image, (5, 10, 150), (0, 0, 30, 50), 5)
        self.rect = self.image.get_rect(topleft=coords)

        self.item = None

        self.inventory = Inventory(display)
        self.inventory.add_item(Gun(display))
        self.inventory.add_item(Bow(display))

        self.bullets = Bullets(display, 10)
        self.arrows = Arrows(display, 10, 0.07)

        self.moving_down_counter = 0
        self.real_moving_down = False  # for platforms 

        self.health = 50
    
    def fire(self, scroll, mx, my):
        mx += scroll[0]
        my += scroll[1]
        if check_if_weapon(self.item):
            if isinstance(self.item, Gun):
                self.bullets.add_bullet(self.rect.center, (mx, my))
            elif isinstance(self.item, Bow):
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
            self.display.blit(self.inventory.draged_item.icon, (mx, my))
    
    def move(self):
        self.movement = [0, 0]
        if self.moving_right:
            self.movement[0] += 3
        if self.moving_left:
            self.movement[0] -= 3
        self.movement[1] += self.player_y_momentum
        self.player_y_momentum += 0.4
        if self.player_y_momentum > 10:
            self.player_y_momentum = 10
        
        if self.real_moving_down:
            self.rect, self.collisions = move(self.rect, self.movement, self.rects)
        else:
            self.rect, self.collisions = move(self.rect, self.movement, self.rects + self.platforms)
        
        if self.moving_down == True:
            self.real_moving_down = True
            self.moving_down_counter = 10
        
        self.moving_down_counter -= 1
        if self.moving_down_counter <= 0:
            self.real_moving_down = False
            self.moving_down_counter = 0


        if self.collisions["top"]:
            self.player_y_momentum = 0
        if self.collisions['bottom']:
            self.player_y_momentum = 0
            self.air_timer = 0
        else:
            self.air_timer += 1

    def update(self, scroll, mx, my, clicked):
        self.move()
        self.display.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))
        self.update_item(scroll, mx, my, self)

        self.draw_healthbar()

        self.update_inventory()
        self.mouse_event(scroll, mx, my, clicked)
    
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
        self.health = 100
    
    def draw_healthbar(self):
        pygame.draw.rect(
            self.display,
            (220, 40, 20),
            (self.WINDOW_SIZE[0] - 280, 30, 250 * (self.health / 100), 30),
            0,
            3)
        pygame.draw.rect(
            self.display,
            (20, 20, 20),
            (self.WINDOW_SIZE[0] - 280, 30, 250, 30),
            2,
            3)


class Enemy_Sniper(Entitiy):
    def __init__(self, display, coords, rects, target):
        Entitiy.__init__(self, display)
        # these points are range of the way which enemy will walk
        self.moving_right = True
        self.point_A = coords[0]
        self.point_B = target

        self.rects = rects

        self.image = pygame.Surface((30, 50))
        self.image.fill((200, 20, 10))
        pygame.draw.rect(self.image, (150, 10, 5), (0, 0, 30, 50), 5)
        self.rect = self.image.get_rect(topleft=coords)

        self.current_item = None
        self.bullets = []
        self.fire_counter = 0
        self.fire_limit = 100

        self.health = 100

    def draw_health(self, scroll):
        green = int(self.health * 2.55)
        pygame.draw.rect(self.display, (255 - green, green, 0),
                         (self.rect.centerx - scroll[0] - 15, self.rect.y - scroll[1] - 15, 0.3 * self.health, 10))
        pygame.draw.rect(self.display, (0, 0, 0),
                         (self.rect.centerx - scroll[0] - 15, self.rect.y - scroll[1] - 15, 30, 10), 1)

    def move(self):
        self.movement = [0, 0]
        if self.moving_right:
            self.movement[0] += 2
        if self.moving_left:
            self.movement[0] -= 2
        self.movement[1] += self.player_y_momentum
        self.player_y_momentum += 0.4
        if self.player_y_momentum > 10:
            self.player_y_momentum = 10

        previous_coord = self.rect.x
        self.rect, self.collisions = move(self.rect, self.movement, self.rects)

        # bot moving algorithm
        if self.moving_right:
            if self.rect.x >= self.point_B or previous_coord == self.rect.x:
                self.moving_right = False
                self.moving_left = True
        elif self.moving_left:
            if self.rect.x <= self.point_A or previous_coord == self.rect.x:
                self.moving_left = False
                self.moving_right = True

        if self.collisions["top"]:
            self.player_y_momentum = 0
        if self.collisions['bottom']:
            self.player_y_momentum = 0
            self.air_timer = 0
        else:
            self.air_timer += 1

    def update_bullets(self, scroll):
        i = 0
        while i < len(self.bullets):
            self.bullets[i].update(scroll)
            if self.bullets[i].collided(self.rects) >= 0:
                del self.bullets[i]
            else:
                i += 1

    def fire(self, display, scroll, rect):
        self.bullets.append(self.current_item.bullet(self.rect.x + 28, self.rect.y + 32,
                                                     rect.centerx, rect.centery, 6, display, scroll))

    def update(self, scroll):
        self.move()
        self.update_bullets(scroll)

        self.display.blit(pygame.transform.flip(self.image, self.player_flip, False),
                     (self.rect.x - scroll[0], self.rect.y - scroll[1]))
        self.draw_health(scroll)


class Enemies:
    def __init__(self, display, rects):
        self.display = display
        self.rects = rects
        self.enemies = list()
    
    def kill_all(self):
        self.enemies.clear()
    
    def update(self, scroll, bullets, arrows):
        i = 0
        while i < len(self.enemies):
            self.enemies[i].update(scroll)
            k = 0
            while k < len(bullets.bullets):
                if bullets.bullets[k].get_hitbox().colliderect(self.enemies[i].rect):
                    self.enemies[i].health -= bullets.bullets[k].damage
                    del bullets.bullets[k]
                    if self.enemies[i].health <= 0:
                        del self.enemies[i]
                        i -= 1
                        break
                    k -= 1
                k += 1
            
            k = 0
            while k < len(arrows.arrows):
                if arrows.arrows[k].get_hitbox().colliderect(self.enemies[i].rect):
                    self.enemies[i].health -= arrows.arrows[k].damage
                    del arrows.arrows[k]
                    if self.enemies[i].health <= 0:
                        del self.enemies[i]
                        i -= 1
                        break
                    k -= 1
                k += 1
            
            i += 1
    
    def add_enemy(self, coords, target):
        self.enemies.append(Enemy_Sniper(self.display, coords, self.rects, target))
