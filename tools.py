import pygame
import math
import sys
import random
from time import sleep
from typing import Callable


from data.font.font import *


def load_image(file_name: str, *, ext: str='png', color_key: tuple | bool=True, scale: tuple=()) -> pygame.Surface:
    image = pygame.image.load(f'{file_name}.{ext}').convert()
    if color_key:
        image.set_colorkey((255, 255, 255))
    if scale:
        image = pygame.transform.scale(image, (image.get_width() * scale[0], image.get_height() * scale[1]))
    return image


# animation_functions_start_________________________________________________#
def load_animation(path, frame_durations, animation_frames) -> list:
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id
        animation_image = load_image(img_loc, scale=(3, 3))
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data


def change_action(action_var, frame, new_value) -> tuple:
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var, frame


# animation_functions_end___________________________________________________#


# collide_functions_start___________________________________________________#
def collision_test(rect: pygame.Rect, tiles: list) -> list:
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile.rect):
            hit_list.append(tile)
    return hit_list


def move(rect: pygame.Rect, movement: tuple, tiles) -> tuple:
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    hit_list = [tile for tile in hit_list if (not tile.ramp) and (not tile.platform)]
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.rect.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.rect.bottom
            collision_types['top'] = True
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    ramps = [tile for tile in hit_list if tile.ramp]

    platforms = [tile for tile in hit_list if tile.platform]

    hit_list = [tile for tile in hit_list if (not tile.ramp) and (not tile.platform)]
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.rect.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.rect.right
            collision_types['left'] = True

    for ramp in ramps:
        hitbox = ramp.rect
        if rect.colliderect(hitbox):
            rel_x = rect.x - hitbox.x
            if ramp.tile_type == "r":
                pos_height = rel_x + rect.width
            else:
                pos_height = 30 - rel_x

            pos_height = min(pos_height, 30)
            pos_height = max(pos_height, 0)
            target_y = hitbox.y + 30 - pos_height

            if rect.bottom > target_y:
                rect.bottom = target_y
                collision_types["bottom"] = True
    
    # platforms
    if movement[1] > 0:
        bottom_rect = pygame.Rect(*rect.bottomleft, rect.width, 1)
        for platform in platforms:
            hitbox = platform.rect
            if bottom_rect.colliderect(hitbox) and abs(rect.bottom - hitbox.y) < 16:  # 16 - maximum "y" movement 
                bottom_rect.bottom = platform.rect.top
                rect.bottom = platform.rect.top
                collision_types['bottom'] = True
    
    return rect, collision_types

# collide_functions_end_____________________________________________________#


class Button(pygame.sprite.Sprite):
    def __init__(self, image, pressed_image, coords, display, sound):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.pressed = pressed_image
        self.rect = self.image.get_rect(topleft=coords)
        self.mouse_on = False
        self.display = display
        self.sound = sound

    def update(self):
        if self.mouse_on:
            self.display.blit(self.pressed, self.rect)
        else:
            self.display.blit(self.image, self.rect)

    def collided(self, mx, my):
        previous_mouse = self.mouse_on
        if self.rect.collidepoint((mx, my)):
            self.mouse_on = True
        else:
            self.mouse_on = False
        if (not previous_mouse) and self.mouse_on:
            self.sound.play()
        return self.mouse_on

    def change_coords(self, coords):
        self.rect = self.image.get_rect(topleft=coords)


# trigonometry functions
def to_deg(rad: float) -> float:
    return rad * (180 / math.pi)


def to_rad(deg: float) -> float:
    return deg * (math.pi / 180)


# function for chance in the game
def chance(num: float = 1.00) -> int:
    return random.randrange(0, 101) <= (round(num, 2) * 100)
