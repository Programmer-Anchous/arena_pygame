from tools import *
from weapon import *


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
                self.cells.append(pygame.Rect(k * 70 + 30, i * 70 + 30, 60, 60))
        
        self.current_item = 0

        self.draged = False
        self.draged_item = None
    
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
        self.player_flip = False
        self.player_y_momentum = 0
        self.air_timer = 0
        self.player_action = None
        self.player_image_id = None
        self.tile_rects = None
        self.collisions = None


# circular motion
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


class Player(pygame.sprite.Sprite):
    def __init__(self, display, coords, rects):
        Entitiy.__init__(self, display)
        self.rects = rects
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
    
    def fire(self, scroll, mx, my):
        mx += scroll[0]
        my += scroll[1]
        if check_if_weapon(self.item):
            if isinstance(self.item, Gun):
                self.bullets.add_bullet(self.rect.center, (mx, my))
            elif isinstance(self.item, Bow):
                self.arrows.add_arrow(self.rect.center, (mx, my))
    
    def update_item(self, scroll, mx, my, player):
        self.bullets.update(scroll)
        self.arrows.update(scroll)
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

        self.rect, self.collisions = move(self.rect, self.movement, self.rects)

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

        self.update_inventory()
        self.mouse_event(scroll, mx, my, clicked)
    
    def update_inventory(self):
        self.inventory.update()
    
    def change_inventory(self):
        self.inventory.is_opened = not self.inventory.is_opened

    def scroll_inventory(self, num):
        self.inventory.scrolling(num)



