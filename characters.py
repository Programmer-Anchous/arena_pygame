from tools import *


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


class Player(pygame.sprite.Sprite):
    def __init__(self, display, coords, rects):
        Entitiy.__init__(self, display)
        self.rects = rects
        self.image = pygame.Surface((30, 50))
        self.image.fill((10, 20, 200))
        pygame.draw.rect(self.image, (5, 10, 150), (0, 0, 30, 50), 5)
        self.rect = self.image.get_rect(topleft=coords)
        
    
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

    def update(self, scroll):
        self.move()
        self.display.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))