import numpy as np
import matplotlib.pyplot as plt
import heapq
import random

NUM_CARS = 100
ALPHA = 0.5
ITERATIONS = 100

HIGHWAY_SPEED = 1.0
LOCAL_SPEED = 0.5
SHORTCUT_SPEED = 0.1


class City:
    def __init__(self, name):
        self.name = name
        self.out_roads = []

    def connect(self, road):
        self.out_roads.append(road)


class Road:
    def __init__(self, start, end, base_time, road_type="local"):
        self.start = start
        self.end = end
        self.base_time = base_time
        self.road_type = road_type
        self.cars = 0

        start.connect(self)

    def travel_time(self):
        if self.road_type == "constant":
            return self.base_time
        return self.base_time + ALPHA * self.cars


class Car:
    def __init__(self, start, goal):
        self.start = start
        self.goal = goal

    def choose_road(self):
        counter = 0
        pq = []
        heapq.heappush(pq, (0, counter, self.start, None))
        visited = {}

        while pq:
            cost, _, city, first_road = heapq.heappop(pq)

            if city in visited and visited[city] <= cost:
                continue
            visited[city] = cost

            if city == self.goal:
                return first_road

            for road in city.out_roads:
                next_city = road.end
                next_cost = cost + road.travel_time()

                if city == self.start:
                    next_first = road
                else:
                    next_first = first_road

                counter += 1
                heapq.heappush(pq, (next_cost, counter, next_city, next_first))

        return None


class Simulation:
    def __init__(self):
        self.setup()

    def setup(self):
        self.S = City("S")
        self.A = City("A")
        self.B = City("B")
        self.T = City("T")

        self.roads = [
            Road(self.S, self.A, LOCAL_SPEED, "local"),
            Road(self.S, self.B, HIGHWAY_SPEED, "constant"),
            Road(self.A, self.T, HIGHWAY_SPEED, "constant"),
            Road(self.B, self.T, LOCAL_SPEED, "local"),
            Road(self.A, self.B, SHORTCUT_SPEED, "constant"),
        ]

        self.cars = [Car(self.S, self.T) for _ in range(NUM_CARS)]

    def reset_flows(self):
        for r in self.roads:
            r.cars = 0

    def step(self):
        self.reset_flows()

        choices = []
        total_time = 0

        # Each car chooses route
        for car in self.cars:
            first_road = car.choose_road()
            choices.append(first_road)
            first_road.cars += 1

        # Estimate travel times after assignment
        for road in self.roads:
            total_time += road.travel_time() * road.cars

        avg_time = total_time / NUM_CARS

        return choices, avg_time


# =========================
# RUN EXPERIMENT
# =========================

sim = Simulation()

avg_times = []
route_counts = []

for i in range(ITERATIONS):
    choices, avg_time = sim.step()

    avg_times.append(avg_time)

    # Count usage of each outgoing road from S
    count_A = sum(1 for r in choices if r.end.name == "A")
    count_B = sum(1 for r in choices if r.end.name == "B")

    route_counts.append((count_A, count_B))


# =========================
# PLOTTING
# =========================

route_counts = np.array(route_counts)

plt.figure()
plt.plot(avg_times)
plt.title("Average Travel Time per Iteration")
plt.xlabel("Iteration")
plt.ylabel("Time")

plt.figure()
plt.plot(route_counts[:, 0], label="S → A")
plt.plot(route_counts[:, 1], label="S → B")
plt.legend()
plt.title("Route Usage Over Time")
plt.xlabel("Iteration")
plt.ylabel("Number of Cars")

plt.show()