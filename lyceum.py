import pygame
import sys
from random import shuffle


WHITE = (230, 230, 230)
BLACK = (0, 0, 0)
RED = (220, 10, 10)
GREEN = (10, 255, 10)

pygame.init()

WSIZE = (500, 800)

screen = pygame.display.set_mode(WSIZE)
pygame.display.set_caption("Дедушка сапёра")

clock = pygame.time.Clock()
FPS = 100

font = pygame.font.Font(None, 40)


def get_cells_around(i, k, matrix):
    leni = len(matrix)
    lenk = len(matrix[0])
    counter = 0
    iterations = (
        (i - 1, k - 1),
        (i - 1, k + 0),
        (i - 1, k + 1),
        (i + 0, k - 1),
        (i + 0, k + 1),
        (i + 1, k - 1),
        (i + 1, k + 0),
        (i + 1, k + 1),
    )
    for i0, k0 in iterations:
        if 0 <= i0 < leni and 0 <= k0 < lenk:
            if matrix[i0][k0] == -2:
                counter += 1
    return counter


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        # значения по умолчанию
        self.left = 10
        self.top = 10
        self.cell_size = 30

        self.cache = []

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, display):
        for y in range(self.height):
            for x in range(self.width):
                rect = (
                    x * self.cell_size + self.left,
                    y * self.cell_size + self.top,
                    self.cell_size,
                    self.cell_size,
                )
                if self.board[y][x] == -2:
                    pygame.draw.rect(display, RED, rect)
                elif self.board[y][x] > 0:
                    screen.blit(
                        font.render(str(self.board[y][x]), True, GREEN),
                        (rect[0] + 10, rect[1] + 10),
                    )
                pygame.draw.rect(display, WHITE, rect, 1)

    def get_cell(self, mouse_pos):
        mx, my = mouse_pos
        for y in range(self.height):
            for x in range(self.width):
                rect = (
                    x * self.cell_size + self.left,
                    y * self.cell_size + self.top,
                    self.cell_size,
                    self.cell_size,
                )
                if rect[0] <= mx <= (rect[0] + rect[2]) and rect[1] <= my <= (
                    rect[1] + rect[3]
                ):
                    return x, y

    def on_click(self, cell_coords):
        if cell_coords:
            x, y = cell_coords
            if self.board[y][x] == -1:
                self.board[y][x] = get_cells_around(y, x, self.board)
                if self.board[y][x] == 0:
                    leni = len(self.board)
                    lenk = len(self.board[0])
                    iterations = (
                        (y - 1, x - 1),
                        (y - 1, x + 0),
                        (y - 1, x + 1),
                        (y + 0, x - 1),
                        (y + 0, x + 1),
                        (y + 1, x - 1),
                        (y + 1, x + 0),
                        (y + 1, x + 1),
                    )
                    for i, k in iterations:
                        if 0 <= i < leni and 0 <= k < lenk:
                            if self.board[i][k] == -1:
                                if (k, i) not in self.cache:
                                    self.on_click((k, i))
                                    self.cache.append((k, i))

    def get_click(self, mouse_pos):
        self.cache.clear()
        self.on_click(self.get_cell(mouse_pos))


class MinesWeaper(Board):
    def __init__(self, width, height, mines):
        Board.__init__(self, width, height)
        cells = width * height
        board = [-1] * (cells - mines) + [-2] * mines
        shuffle(board)
        for i in range(height):
            for k in range(width):
                self.board[i][k] = board[i * width + k]

    def open_cell(self, coords):
        board.get_click(coords)


board = MinesWeaper(9, 15, 20)
board.set_view(25, 25, 50)

running = True
while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                board.open_cell(pygame.mouse.get_pos())

    board.render(screen)

    pygame.display.update()
    clock.tick(FPS)
