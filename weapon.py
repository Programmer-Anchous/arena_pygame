from tools import *


class Arrow(pygame.sprite.Sprite):
    def __init__(self, display: pygame.Surface, start: tuple, end: tuple, speed: int, gravity: int):
        self.x, self.y = start

        targetx, targety = end
        angle = math.atan2(targety - self.y, targetx - self.x)
        degrees = round(to_deg(angle))

        self.origin_image = load_image("data/arrow_im", color_key=(255, 255, 255))
        self.image = pygame.transform.rotate(self.origin_image, -degrees)

        self.rect = pygame.Rect(0, 0, 4, 4)

        self.hitbox = pygame.Rect(0, 0, 1, 1)  # no hitbox in the start

        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed

        self.display = display

        self.current_gravity = 0

        self.gravity = gravity
    
    def update(self):

        self.current_gravity += self.gravity

        self.x = self.x + self.dx
        self.y = self.y + self.dy + self.current_gravity

        degrees = to_deg(math.atan2(self.dy + self.current_gravity, self.dx))
        self.image = pygame.transform.rotate(self.origin_image, -degrees)

        self.rect.center = (self.x, self.y)
        self.display.blit(self.image,
                          (self.rect.x - self.image.get_width() // 2,
                           self.rect.y - self.image.get_height() // 2))
        


        x0, y0 = self.rect.center
        x1 = math.cos(to_rad(degrees)) * 25 + x0 - 6
        y1 = math.sin(to_rad(degrees)) * 25 + y0 - 6

        self.hitbox = pygame.Rect(x1, y1, 10, 10)
    
    def get_hitbox(self):
        return self.hitbox


class Lightning(pygame.sprite.Sprite):
    def __init__(self, display: pygame.Surface, window_size: tuple):
        self.display = display
        self.origin_start = None

        self.surf = pygame.Surface(window_size)
        self.surf.set_colorkey((0, 0, 0))
        self.dark_surf = pygame.Surface(window_size)
        self.light = 0

        self.electicity_sound = pygame.mixer.Sound("data/electricity.mp3")
        self.electicity_sound.set_volume(0.2)
        
    def generate_points(self):
        self.segment_list = self.origin_start.copy()

        self.offset_amount = 100

        self.light = 0

        for _ in range(7):
            length = len(self.segment_list)
            i = 0
            for i in range(length - 1):
                p1, p2 = self.segment_list[i * 2], self.segment_list[i * 2 + 1]
                angle = math.atan2(p2[0] - p1[0], p2[1] - p1[1])
                offset = random.choice((-1, 1)) * self.offset_amount
                mid_x = int((p1[0] + p2[0]) / 2 + math.cos(angle) * offset)
                mid_y = int((p1[1] + p2[1]) / 2 - math.sin(angle) * offset)
                mid_point = (mid_x, mid_y)
                self.segment_list.insert(i * 2 + 1, mid_point)
            self.offset_amount //= 2
    
    def new_lightning(self, start, end):
        # self.electicity_sound.play()
        self.origin_start = [start, end]
        self.generate_points()
        self.light = 255

    def update(self):
        self.light -= 4
        if self.light <= 0:
            self.light = 0
        if self.light:
            self.surf.fill((0, 0, 0))
            self.surf.set_alpha(self.light)

            self.dark_surf.set_alpha(self.light // 2)
            self.display.blit(self.dark_surf, (0, 0))
            pygame.draw.lines(self.surf, (100, 120, 155), False, self.segment_list, 4)
            pygame.draw.lines(self.surf, (220, 230, 255), False, self.segment_list, 2)
            self.display.blit(self.surf, (0, 0))


class Lightning1(pygame.sprite.Sprite):
    def __init__(self, display: pygame.Surface, start: tuple, end: tuple):
        self.display = display
        self.points = [start, end]

        self.counter = 0

        for _ in range(1, 20):
            n = random.randrange(len(self.points) - 1)

            p1 = self.points[n]
            p2 = self.points[n + 1]

            angle = math.atan2(p2[0] - p1[0], p2[1] - p1[1])
            
            offset = 1 / random.randrange(1, 4) * 30

            side = random.choice((-1, 1))
            dx = offset * math.cos(angle) * side
            dy = offset * math.sin(angle) * -side

            x = int((p2[0] + p1[0]) / 2 + dx)
            y = int((p2[1] + p1[1]) / 2 + dy)
            self.points.insert(n + 1, (x, y))
    
    def update(self, start, end):
        # self.counter += 1
        # if self.counter >= 2:
        #     if len(self.points) > 10 and math.hypot(start[0] - end[0], start[1] - end[1]) < 300:
        #         self.del_point()
        #     elif len(self.points) < 25 and math.hypot(start[0] - end[0], start[1] - end[1]) > 300:
        #         self.add_point()
        #     self.points[0] = start
        #     self.points[-1] = end
        #     self.counter = 0
        #     used = []
        #     for _ in range(1, len(self.points)):
        #         n = random.randrange(1, len(self.points) - 1)

        #         if n in used:
        #             continue
        #         else:
        #             used.append(n)
        #         p1 = self.points[n - 1]
        #         p2 = self.points[n + 1]

        #         angle = math.atan2(p2[0] - p1[0], p2[1] - p1[1])
                
                
        #         offset = 1 / random.randrange(1, 4) * 8
        #         if offset > 40:
        #             print(offset, n)

        #         side = random.choice((-1, 1))
        #         dx = offset * math.cos(angle) * side
        #         dy = offset * math.sin(angle) * -side

        #         x = int((p2[0] + p1[0]) / 2 + int(dx))
        #         y = int((p2[1] + p1[1]) / 2 + int(dy))

        #         self.points[n] = (x, y)
        pygame.draw.lines(self.display, (80, 120, 255), False, self.points, 3)
        pygame.draw.lines(self.display, (190, 210, 255), False, self.points, 2)
        

    def del_point(self):
        del self.points[len(self.points) // 2]
    
    def add_point(self):
        self.points.insert(-3, self.points[-2])    


class Arrows:
    def __init__(self, display: pygame.Surface, speed: int , gravity: int):
        self.display = display
        self.speed = speed
        self.gravity = gravity
        self.arrows = list()
    
    def update(self):
        i = 0
        while i < len(self.arrows):
            self.arrows[i].update()
            x, y = self.arrows[i].rect.center
            if not ((-2000 < x < 2000) and (-2000 < y < 2000)):
                del self.arrows[i]
            else:
                i += 1
    
    def add_arrow(self, start: tuple, end: tuple):
        self.arrows.append(Arrow(self.display, start, end, self.speed, self.gravity))