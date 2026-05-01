import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import random

# --- Parameters calibrated for the Paradox ---
NUM_CARS = 4000 
ITERATIONS = 60
LEARNING_RATE = 0.2 

class City:
    def __init__(self, name, pos):
        self.name = name
        self.pos = pos
        self.out_roads = []

    def connect(self, road):
        self.out_roads.append(road)

class Road:
    def __init__(self, start, end, road_type):
        self.start = start
        self.end = end
        self.road_type = road_type
        self.cars = 0
        start.connect(self)

    def travel_time(self):
        if self.road_type == "bottleneck":
            return self.cars / 100
        elif self.road_type == "highway":
            return 45
        elif self.road_type == "shortcut":
            return 0
        return 0

    def get_label(self):
        t = self.travel_time()
        if self.road_type == "bottleneck":
            return f"x/100\nTime: {t:.1f}"
        if self.road_type == "highway":
            return f"45\nTime: {t:.1f}"
        return f"0\nTime: {t:.1f}"

class Simulation:
    def __init__(self, include_shortcut=True):
        self.S = City("S", pos=(0, 1))
        self.A = City("A", pos=(1, 2))
        self.B = City("B", pos=(1, 0))
        self.T = City("T", pos=(2, 1))

        self.roads = [
            Road(self.S, self.A, "bottleneck"),
            Road(self.S, self.B, "highway"),
            Road(self.A, self.T, "highway"),
            Road(self.B, self.T, "bottleneck"),
        ]
        if include_shortcut:
            self.roads.append(Road(self.A, self.B, "shortcut"))
            
        # Initial state: Randomly assign paths to start
        self.car_paths = [random.choice(self.get_available_paths()) for _ in range(NUM_CARS)]
        self.pos = {city.name: city.pos for city in [self.S, self.A, self.B, self.T]}

    def get_available_paths(self):
        paths = [
            [self.roads[0], self.roads[2]], # S-A-T
            [self.roads[1], self.roads[3]]  # S-B-T
        ]
        if len(self.roads) > 4:
            paths.append([self.roads[0], self.roads[4], self.roads[3]]) # S-A-B-T (The Trap)
        return paths

    def step(self):
        for r in self.roads: r.cars = 0
        
        for path in self.car_paths:
            for road in path:
                road.cars += 1
        
        available_paths = self.get_available_paths()
        path_times = [sum(r.travel_time() for r in p) for p in available_paths]
            
        best_path_idx = np.argmin(path_times)
        best_path = available_paths[best_path_idx]
        
        # Drivers switch paths if a better one is found
        for i in range(NUM_CARS):
            if random.random() < LEARNING_RATE:
                self.car_paths[i] = best_path
                
        # Calculate the real average time experienced by all cars
        total_time = sum(sum(r.travel_time() for r in p) for p in self.car_paths)
        return total_time / NUM_CARS

    def draw_network(self, i, avg_time):
        plt.subplot(1, 2, 1) # Left side: Network
        plt.cla()
        G = nx.DiGraph()
        edge_labels = {}
        for r in self.roads:
            G.add_edge(r.start.name, r.end.name)
            edge_labels[(r.start.name, r.end.name)] = r.get_label()
        
        nx.draw(G, self.pos, with_labels=True, node_size=1000, node_color='orange', 
                font_weight='bold', arrows=True, connectionstyle='arc3, rad = 0.1')
        nx.draw_networkx_edge_labels(G, self.pos, edge_labels=edge_labels, font_size=15)
        plt.title(f"Traffic Network (Iter {i})")

# --- Execute ---
sim = Simulation(include_shortcut=True)
history = []

plt.ion()
fig = plt.figure(figsize=(14, 6))

for i in range(ITERATIONS):
    avg_time = sim.step()
    history.append(avg_time)
    
    if i % 1 == 0:
        sim.draw_network(i, avg_time)
        
        # Right side: Equilibrium Graph
        plt.subplot(1, 2, 2)
        plt.plot(history, color='red', linewidth=2)
        plt.title(f"Equilibrium Graph: Avg Time = {avg_time:.2f} min")
        plt.xlabel("Iteration")
        plt.ylabel("Avg Travel Time")
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.pause(0.01)

plt.ioff()
print(f"Final Equilibrium Travel Time: {history[-1]:.2f} minutes")
plt.show()