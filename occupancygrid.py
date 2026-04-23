import numpy as np
import pygame as pg

class OccupancyGrid:
    def __init__(self, world_size, cell_size):
        self.world_size = world_size
        self.cell_size = cell_size

        self.cols = world_size // cell_size
        self.rows = world_size // cell_size

        # 0 = free, 1 = wall
        self.grid = np.zeros((self.rows, self.cols), dtype=int)

        self._generate_maze()

    def _generate_maze(self):
        """Simple hardcoded maze (you can replace later)"""
        # Borders
        self.grid[0, :] = 1
        self.grid[-1, :] = 1
        self.grid[:, 0] = 1
        self.grid[:, -1] = 1

        # Some internal walls
        for i in range(5, self.cols - 5):
            self.grid[10, i] = 1

        for i in range(5, self.rows - 5):
            self.grid[i, 15] = 1

    def world_to_grid(self, x, y):
        """Convert pixel → grid index"""
        col = int(x // self.cell_size)
        row = int(y // self.cell_size)
        return row, col

    def is_occupied(self, x, y):
        row, col = self.world_to_grid(x, y)

        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row, col] == 1
        return True  # outside = wall

    def draw(self, surface):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row, col] == 1:
                    rect = pg.Rect(
                        col * self.cell_size,
                        row * self.cell_size,
                        self.cell_size,
                        self.cell_size
                    )
                    pg.draw.rect(surface, (100, 100, 100), rect)