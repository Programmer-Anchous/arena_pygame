from tools import *


class Loop:
    def __init__(self, WINDOW_SIZE: tuple | None = None, FPS: int = 60, font_path: None | str = None):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()

        if WINDOW_SIZE:
            self.WINDOW_SIZE = WINDOW_SIZE
            self.screen = pygame.display.set_mode(self.WINDOW_SIZE)
        else:
            WINDOW_SIZE = pygame.display.Info()
            self.WINDOW_SIZE = (WINDOW_SIZE.current_w, WINDOW_SIZE.current_h)
            self.screen = pygame.display.set_mode(self.WINDOW_SIZE, pygame.FULLSCREEN)
        
        self.FPS = FPS
        
        self.display = pygame.Surface(self.WINDOW_SIZE)
        self.clock = pygame.time.Clock()

        self.events = None
        self.running = True

        if font_path:
            self.font2 = Font(font_path, 2)
            self.font3 = Font(font_path, 3)
        
        self.user_init()

        self.loop_on = True
    
    def run(self):
        if self.loop_on:
            while self.running:
                if not self.loop_on:
                    self.running = False
                self.display.fill((0, 0, 0))

                self.action()

                self.user_events()

                self.screen.blit(self.display, (0, 0))
                pygame.display.update()
                self.clock.tick(self.FPS)
            self.user_end_action()
    
    def action(self):
        self.events = pygame.event.get()

    def get_events(self):
        return self.events
    
    # user function
    def user_init(self):
        pass
    
    # user function
    def user_events(self):
        pass

    # user function
    def user_end_action(self):
        pass