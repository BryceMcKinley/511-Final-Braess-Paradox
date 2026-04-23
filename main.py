import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random

# =========================
# CONFIG
# =========================
NUM_CARS = 40
ALPHA = 0.5  # congestion strength

# =========================
# CLASSES
# =========================

class City:
    def __init__(self, name, pos):
        self.name = name
        self.pos = np.array(pos)
        self.out_roads = []

    def connect(self, road):
        self.out_roads.append(road)


class Road:
    def __init__(self, start, end, road_type="local"):
        self.start = start
        self.end = end
        self.road_type = road_type
        self.cars = []

        start.connect(self)

    def travel_time(self):
        if self.road_type == "constant":
            return 1.0
        else:
            return 1.0 + ALPHA * len(self.cars)


class Car:
    def __init__(self, start, goal):
        self.current_city = start
        self.goal = goal
        self.road = None
        self.progress = 0.0

    def choose_road(self):
        # Greedy (selfish routing)
        best_road = None
        best_cost = float('inf')

        for road in self.current_city.out_roads:
            cost = road.travel_time()

            # heuristic: distance to goal
            dist = np.linalg.norm(road.end.pos - self.goal.pos)

            total_cost = cost + dist

            if total_cost < best_cost:
                best_cost = total_cost
                best_road = road

        return best_road

    def update(self, dt):
        if self.road is None:
            if self.current_city == self.goal:
                return  # arrived

            self.road = self.choose_road()
            self.road.cars.append(self)
            self.progress = 0.0

        self.progress += dt / self.road.travel_time()

        if self.progress >= 1.0:
            self.road.cars.remove(self)
            self.current_city = self.road.end
            self.road = None
            self.progress = 0.0

    def get_position(self):
        if self.road is None:
            return self.current_city.pos

        start = self.road.start.pos
        end = self.road.end.pos
        return start + self.progress * (end - start)


# =========================
# SIMULATION
# =========================

class Simulation:
    def __init__(self):
        self.cities = []
        self.roads = []
        self.cars = []

    def setup_braess(self):
        S = City("S", (0, 0.5))
        A = City("A", (0.5, 1))
        B = City("B", (0.5, 0))
        T = City("T", (1, 0.5))

        self.cities = [S, A, B, T]

        self.roads = [
            Road(S, A, "local"),      # congested
            Road(S, B, "constant"),
            Road(A, T, "constant"),
            Road(B, T, "local"),      # congested
            Road(A, B, "constant"),   # shortcut (Braess)
        ]

        for _ in range(NUM_CARS):
            self.cars.append(Car(S, T))

    def update(self, dt):
        for car in self.cars:
            car.update(dt)


# =========================
# VISUALIZATION
# =========================

sim = Simulation()
sim.setup_braess()

fig, ax = plt.subplots()

def draw_arrow(start, end, road_type):
    dx, dy = end - start

    width = 0.01 if road_type == "local" else 0.02

    ax.arrow(start[0], start[1], dx, dy,
             length_includes_head=True,
             head_width=0.05,
             fc='black', ec='black',
             linewidth=2 if road_type == "constant" else 1,
             alpha=0.7)

def draw():
    ax.clear()

    # Draw roads with arrows
    for road in sim.roads:
        draw_arrow(road.start.pos, road.end.pos, road.road_type)

    # Draw cities
    for city in sim.cities:
        ax.scatter(*city.pos, s=100)
        ax.text(city.pos[0], city.pos[1] + 0.05, city.name, ha='center')

    # Draw cars
    for car in sim.cars:
        pos = car.get_position()
        ax.scatter(*pos, c='red', s=15)

    ax.set_xlim(-0.2, 1.2)
    ax.set_ylim(-0.2, 1.2)
    ax.set_aspect('equal')


def update(frame):
    sim.update(dt=0.05)
    draw()

ani = FuncAnimation(fig, update, frames=300, interval=50)
plt.show()