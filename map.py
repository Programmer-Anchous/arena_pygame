from tools import *


class Tile:
    def __init__(self, rect, tile_type, ramp=False):
        self.rect = rect
        self.tile_type = tile_type
        self.ramp = ramp


class Map:
    def __init__(self, display, filename):
        self.display = display
        self.tile_rects = []
        self.tile_width = 30

        block_center = pygame.Surface((self.tile_width, self.tile_width))
        pygame.draw.rect(block_center, (100, 100, 100), (0, 0, 30, 30))
        pygame.draw.rect(block_center, (50, 50, 50), (0, 0, 30, 30), 5)

        left_ramp = pygame.Surface((self.tile_width, self.tile_width))
        pygame.draw.polygon(left_ramp, (50, 50, 50), ((0, 0), (30, 30), (0, 30)))
        left_ramp.set_colorkey((0, 0, 0))

        right_ramp = pygame.Surface((self.tile_width, self.tile_width))
        pygame.draw.polygon(right_ramp, (50, 50, 50), ((30, 0), (30, 30), (0, 30)))
        right_ramp.set_colorkey((0, 0, 0))

        self.tile_index = {
            "s": block_center,
            "l": left_ramp,
            "r": right_ramp
        }

        with open(filename, "r", encoding="utf-8") as file:
            self.data = file.read().split("\n")
        
        for i in range(len(self.data)):
            for k in range(len(self.data[i])):
                if self.data[i][k] in "rl":
                    self.tile_rects.append(
                        Tile(pygame.Rect(k * self.tile_width, i * self.tile_width, self.tile_width, self.tile_width),
                             self.data[i][k], True))
                elif self.data[i][k] != " ":
                    self.tile_rects.append(
                        Tile(pygame.Rect(k * self.tile_width, i * self.tile_width, self.tile_width, self.tile_width),
                             self.data[i][k], False))
        
        self.block_img = pygame.Rect(0, 0, 30, 30)
    
    def update(self, scroll):
        for i in range(len(self.data)):
            for k in range(len(self.data[i])):
                if self.data[i][k] != " ":
                    self.display.blit(self.tile_index[self.data[i][k]],
                    (k * self.tile_width - scroll[0], i * self.tile_width - scroll[1]))
    def get_rects(self):
        return self.tile_rects