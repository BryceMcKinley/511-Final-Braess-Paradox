ROBOT_SPEED = 10  # pixels per second
WORLD_SIZE = 1000
import pygame as pg
import numpy as np
import occupancygrid as og

class Robot:
    def __init__(self, id, location, signal_range=10, color='white'):
        self.id = id
        self.location = location
        self.signal_range = signal_range
        self.color = color

    def move(self):
        # Simple random walk for demonstration
        dx = np.random.uniform(-1, 1) * ROBOT_SPEED * 0.1
        dy = np.random.uniform(-1, 1) * ROBOT_SPEED * 0.1
        new_x = np.clip(self.location[0] + dx, 0, WORLD_SIZE)
        new_y = np.clip(self.location[1] + dy, 0, WORLD_SIZE)
        self.location = (new_x, new_y)

    def get_grid_position(self, occupancy_grid):
        return occupancy_grid.world_to_grid(*self.location)
    
    def communicate(self, other):
        dist = np.linalg.norm(np.array(self.location) - np.array(other.location))
        if dist <= self.signal_range:
            print(f"Robot {self.id} communicates with Robot {other.id}")

    def sense(self, occupancy_grid):
        grid_pos = self.get_grid_position(occupancy_grid)
        print(f"Robot {self.id} senses at grid position {grid_pos}")
        

class Eyebot(Robot):
    def __init__(self, id, location):
        super().__init__(id, location)

    def scan(self):
        print(f"Eyebot {self.id} is scanning the area.")

class Footbot(Robot):
    def __init__(self, id, location):
        super().__init__(id, location)

    def climb(self):
        print(f"Footbot {self.id} is climbing an obstacle.")

class Handbot(Robot):
    def __init__(self, id, location):
        super().__init__(id, location)

    def manipulate(self):
        print(f"Handbot {self.id} is manipulating an object.")

class swarmanoid:
    def __init__(self):
        self.robots = []

    def add_robot(self, robot):
        self.robots.append(robot)

    def operate(self):
        for robot in self.robots:
            robot.move()
            if isinstance(robot, Eyebot):
                robot.scan()
            elif isinstance(robot, Footbot):
                robot.climb()
            elif isinstance(robot, Handbot):
                robot.manipulate()
def get_color(color):
    """Convert string colors to pygame RGB"""
    COLORS = {
        'white': (255, 255, 255),
        'red': (255, 80, 80),
        'green': (80, 255, 80),
        'blue': (80, 80, 255),
        'yellow': (255, 255, 80),
        'purple': (200, 80, 255),
    }
    return COLORS.get(color, color)  # allow RGB tuples too

def get_grid_position(self, occupancy_grid):
    return occupancy_grid.world_to_grid(*self.location)