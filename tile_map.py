from tools import *


class Tile:
    def __init__(self, rect, tile_type, ramp=False, platform=False):
        self.rect = rect
        self.tile_type = tile_type
        self.ramp = ramp
        self.platform = platform


class Map:
    def __init__(self, display, filename):
        self.display = display
        self.tile_rects = []
        self.platforms = []
        self.tile_width = 30

        block_center = pygame.Surface((self.tile_width, self.tile_width))
        pygame.draw.rect(block_center, (100, 100, 100), (0, 0, 30, 30))
        pygame.draw.rect(block_center, (50, 50, 50), (0, 0, 30, 30), 5)

        left_ramp = pygame.Surface((self.tile_width, self.tile_width))
        pygame.draw.polygon(left_ramp, (50, 50, 50), ((0, 0), (30, 30), (0, 30)))
        pygame.draw.polygon(left_ramp, (100, 100, 100), ((5, 13), (17, 25), (5, 25)))
        left_ramp.set_colorkey((0, 0, 0))

        platform = pygame.Surface((self.tile_width, self.tile_width))
        pygame.draw.rect(platform, (139, 69, 19), (0, 0, 30, 10))
        pygame.draw.rect(platform, (109, 39, 0), (0, 0, 30, 10), 2)
        platform.set_colorkey((0, 0, 0))

        right_ramp = pygame.transform.flip(left_ramp, True, False)

        right_ramp.set_colorkey((0, 0, 0))

        self.tile_index = {
            "s": block_center,
            "l": left_ramp,
            "r": right_ramp,
            "p": platform
        }
        self.player_spawn = (0, 0)

        with open(filename, "r", encoding="utf-8") as file:
            self.data = file.read().split("\n")
            self.max_width = max(map(len, self.data))
            self.data = list(map(list, self.data))
        
        self.mini_width = 4
        self.minimap = pygame.Surface((self.max_width * self.mini_width + 10, len(self.data) * self.mini_width + 10))
        self.minimap.set_alpha(130)

        for i in range(len(self.data)):
            for k in range(len(self.data[i])):
                if self.data[i][k] == "p":
                    self.platforms.append(
                        Tile(pygame.Rect(k * self.tile_width, i * self.tile_width, self.tile_width, self.tile_width),
                             self.data[i][k], False, True))
                    
                    pygame.draw.rect(
                        self.minimap, (180, 130, 10),
                        pygame.Rect(k * self.mini_width + 5, i * self.mini_width + 5, self.mini_width, self.mini_width)
                    )
                
                elif self.data[i][k] in "rl":
                    self.tile_rects.append(
                        Tile(pygame.Rect(k * self.tile_width, i * self.tile_width, self.tile_width, self.tile_width),
                             self.data[i][k], True))
                    
                    pygame.draw.rect(
                        self.minimap, (200, 200, 200),
                        pygame.Rect(k * self.mini_width + 5, i * self.mini_width + 5, self.mini_width, self.mini_width)
                    )
                
                elif self.data[i][k] == "@":
                        self.player_spawn = (k * self.tile_width, i * self.tile_width)
                        self.data[i][k] = " "
                
                elif self.data[i][k] != " ":
                    self.tile_rects.append(
                        Tile(pygame.Rect(k * self.tile_width, i * self.tile_width, self.tile_width, self.tile_width),
                             self.data[i][k], False))
                    
                    pygame.draw.rect(
                        self.minimap, (200, 200, 200),
                        pygame.Rect(k * self.mini_width + 5, i * self.mini_width + 5, self.mini_width, self.mini_width)
                    )

        self.block_img = pygame.Rect(0, 0, 30, 30)
    
    def get_minimap(self):
        return self.minimap
    
    def update(self, scroll):
        for i in range(len(self.data)):
            for k in range(len(self.data[i])):
                if self.data[i][k] != " ":
                    self.display.blit(self.tile_index[self.data[i][k]],
                    (k * self.tile_width - scroll[0], i * self.tile_width - scroll[1]))
    
    def get_rects(self):
        return self.tile_rects
    
    def get_platforms(self):
        return self.platforms
    
    @classmethod
    def get_minimap_from_file(self, filename: str) -> pygame.Surface:
        with open(filename, "r", encoding="utf-8") as file:
            data = file.read().split("\n")
            max_width = max(map(len, data))
            data = list(map(list, data))
        
            mini_width = 4
            offset = 10
            minimap = pygame.Surface((max_width * mini_width + offset * 2, len(data) * mini_width + offset * 2))

            alpha_surf = pygame.Surface(minimap.get_size())
            pygame.draw.rect(alpha_surf, (20,) * 3, (0, 0, *alpha_surf.get_size()), 0, 7)
            
            alpha_surf.set_colorkey((0, 0, 0))
            alpha_surf.set_alpha(200)

            pygame.draw.rect(minimap, (30,) * 3, (0, 0, *minimap.get_size()), 2, 7)

            for i in range(len(data)):
                for k in range(len(data[i])):
                    if data[i][k] == "p":
                        pygame.draw.rect(
                            minimap, (150, 100, 50),
                            pygame.Rect(k * mini_width + offset, i * mini_width + offset, mini_width, mini_width)
                        )
                    elif data[i][k] in "rls":
                        pygame.draw.rect(
                            minimap, (100, 100, 100),
                            pygame.Rect(k * mini_width + offset, i * mini_width + offset, mini_width, mini_width)
                        )
            
            minimap.set_colorkey((0, 0, 0))

            return minimap, alpha_surf
