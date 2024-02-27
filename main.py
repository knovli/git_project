import pygame
import random


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.left = 10
        self.top = 10
        self.cell_size = 30
        self.endgame = 0

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        color = pygame.Color('white')
        for y in range(self.height):
            for x in range(self.width):
                coor = (x * self.cell_size + self.left, y * self.cell_size + self.top, self.cell_size, self.cell_size)
                pygame.draw.rect(screen, color, coor, 0)

    def get_cell(self, mouse_pos):
        cell_x = (mouse_pos[0] - self.left) // self.cell_size
        cell_y = (mouse_pos[1] - self.top) // self.cell_size
        if cell_x < 0 or cell_x >= self.width or cell_y < 0 or cell_y >= self.height:
            return None
        return cell_x, cell_y

    def on_click(self, cell):
        pass

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell:
            self.on_click(cell)


class Minesweeper(Board):
    def __init__(self, width, height, need):
        super().__init__(width, height)
        self.board = [[-1] * width for inet in range(height)]
        ter = 0
        while ter < need:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.board[y][x] == -1:
                self.board[y][x] = 10
                ter += 1

    def open_click(self, cell):
        if self.endgame != 1:
            x, y = cell
            if self.board[y][x] == 10:
                self.board[y][x] = 11
                self.endgame = 1
                return
            s = 0
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    if x + dx < 0 or x + dx >= self.width or y + dy < 0 or y + dy >= self.height:
                        continue
                    if self.board[y + dy][x + dx] == 10:
                        s += 1
            if s == 0:
                s1 = 0
                for x1 in range(self.width):
                    for y1 in range(self.height):
                        s1 = 0
                        if self.board[y1][x1] == -1:
                            for dy1 in range(-1, 2):
                                for dx1 in range(-1, 2):
                                    if x1 + dx1 < 0 or x1 + dx1 >= self.width or y1 + dy1 < 0 or y1 + dy1 >= self.height:
                                        continue
                                    if self.board[y1 + dy1][x1 + dx1] == 10:
                                        s1 += 1
                            if s1 == 0:
                                self.board[y1][x1] = s1
            self.board[y][x] = s

    def on_click(self, cell):
        self.open_click(cell)

    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                coor = (x * self.cell_size + self.left, y * self.cell_size + self.top,
                        self.cell_size, self.cell_size)
                coor1 = (x * self.cell_size + self.left + 2, y * self.cell_size + self.top + 2,
                         self.cell_size, self.cell_size)
                pygame.draw.rect(screen, pygame.Color('white'), coor, 1)
                if self.board[y][x] >= 0 and self.board[y][x] < 10:
                    font = pygame.font.Font(None, self.cell_size - 7)
                    text = font.render(str(self.board[y][x]), 1, (100, 255, 100))
                    screen.blit(text, coor1)
                elif self.board[y][x] == 11:
                    pygame.draw.rect(screen, pygame.Color('red'), coor)
        pygame.draw.rect(screen, pygame.Color('white'), ((480, 200), (50, 50)), 1)


def main():
    pygame.init()
    size = 550, 472
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('sapper')
    clock = pygame.time.Clock()
    board = Minesweeper(15, 15, 23)
    ticks = 0
    running = True
    while running:
        for event in pygame.event.get():
            mouse = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                board.get_click(event.pos)
                if 480 <= mouse[0] <= 530 and 200 <= mouse[1] <= 250:
                    board = Minesweeper(15, 15, 23)
        screen.fill((0, 0, 0))
        board.render(screen)
        pygame.display.flip()
        clock.tick(50)
        ticks += 1
    pygame.quit()


if __name__ == '__main__':
    main()