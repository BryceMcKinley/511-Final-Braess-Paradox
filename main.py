import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import random
import copy

# --- Parameters calibrated for the Paradox ---
NUM_CARS = 4000 
ITERATIONS = 60
ALTRUISTIC_PERCENTAGE = 0.005

INCLUDE_SHORTCUT = True
RNDM_SWITCH = False

DELETE_SHORTCUT_HALF_WAY = True

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
        elif self.road_type == "broken":
            return 200 # High penalty value
        return 0

    def get_label(self):
        t = self.travel_time()
        if self.road_type == "bottleneck":
            return f"x/100\nTime: {t:.1f}\nCars: {self.cars}"
        if self.road_type == "highway":
            return f"45\nTime: {t:.1f}\nCars: {self.cars}"
        return f"0\nTime: {t:.1f}\nCars: {self.cars}"

class Simulation:
    def __init__(self, include_shortcut=True):
        self.learning_rate = 0.2
        self.step_count = 1
        
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

    def step(self, info=False, avg=False, rndm=RNDM_SWITCH):
        """
        if info:
            SAT = 45 + xa/100
            SBT = 45 + xb/100
            SABT = (xa + xb)/100"""
        
        for r in self.roads: r.cars = 0
        
        for path in self.car_paths:
            for road in path:
                road.cars += 1
        
        available_paths = self.get_available_paths()
        path_times = [sum(r.travel_time() for r in p) for p in available_paths]
            
        best_path_idx = np.argmin(path_times)
        best_path = available_paths[best_path_idx]
        
        # Calculating Learning Rate
        car_speeds = [sum(r.travel_time() for r in p) for p in self.car_paths]
        std = np.std(car_speeds)
        if std * 0.1 < self.learning_rate:
            self.learning_rate = std * 0.1 - (self.step_count/ITERATIONS) * 0.0001
        self.step_count += 1
        print(f"Learning Rate: {self.learning_rate:.4f} | Std Dev of Car Speeds: {std:.2f}")

        if it == 0:
            self.it_car_speeds = [sum(r.travel_time() for r in p) for p in self.car_paths]
        temp_speeds = [sum(r.travel_time() for r in p) for p in self.car_paths]

        for i in range(NUM_CARS):
            if random.random() < self.learning_rate:
                self.car_paths[i] = best_path
            if rndm:
                # Introduce a "Frustration Probability"
                # Only a small % of cars that are over their initial time will actually switch
                if temp_speeds[i] > self.it_car_speeds[i]:
                    if random.random() < 0.05:  # Only 5% of frustrated cars switch per iteration
                        available = [x for x in self.get_available_paths() if x != self.car_paths[i]]
                        self.car_paths[i] = random.choice(available)
            if random.random() < ALTRUISTIC_PERCENTAGE:
                # These cars avoid the 'Trap' (S-A-B-T) because they "know" it ruins the average
                self.car_paths[i] = random.choice([available_paths[0], available_paths[1]])
            
            
                
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
        nx.draw_networkx_edge_labels(
                G, sim.pos, ax=ax1, 
                edge_labels=edge_labels, 
                font_size=20,           # Slightly larger for readability
                font_weight='bold',
                label_pos=0.5,)
        plt.title(f"Traffic Network (Iter {i})")    

# --- Execute ---
sim = Simulation(include_shortcut=INCLUDE_SHORTCUT)
history = []
cars_sat = []
cars_sbt = []
cars_sabt = []

plt.ion()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8), dpi=90)
plt.subplots_adjust(left=0.05, right=0.5, top=0.5, bottom=0.1, wspace=0.3)
ax2.axis('off')

for i in range(ITERATIONS):
    if DELETE_SHORTCUT_HALF_WAY and i == ITERATIONS // 2:
        if len(sim.roads) > 4:
            sim.roads[4].road_type = "broken"
    it = i
    avg_time = sim.step()
    history.append(avg_time)
    cars_sat.append(sim.roads[2].cars)
    cars_sbt.append(sim.roads[1].cars)
    cars_sabt.append(sim.roads[0].cars - sim.roads[2].cars)
    cars_all = cars_sat[i] + cars_sbt[i] + cars_sabt[i]
    
    if i % 1 == 0:
        sim.draw_network(i, avg_time)
        
        # Right top: Equilibrium Graph
        plt.subplot(2, 2, 2)
        plt.plot(history, color='red', linewidth=2)
        plt.ylim(60, 90)
        plt.title(f"Equilibrium Graph: Avg Time = {avg_time:.2f} min")
        plt.xlabel("Iteration")
        plt.ylabel("Avg Travel Time")
        plt.grid(True, alpha=0.3)
        
        #Right bottom: Number of Cars per Path Graph
        plt.subplot(2, 2, 4)
        plt.plot(cars_sat, color='red', linewidth=2, label='S-A-T')
        plt.plot(cars_sbt, color='green', linewidth=2, label='S-B-T')
        plt.plot(cars_sabt, color='blue', linewidth=2, label='S-A-B-T')
        plt.ylim(0, 4000)
        plt.title(f"Number of Cars Per Path Graph: Total Cars = {cars_all}")
        plt.xlabel("Iteration")
        plt.ylabel("Number of Cars Per Path")
        plt.grid(True, alpha=0.3)
        handles, labels = plt.gca().get_legend_handles_labels()
        plt.legend(handles[:3], labels[:3])

        
        plt.tight_layout()
        plt.pause(0.01)

plt.ioff()
print(f"Final Equilibrium Travel Time: {history[-1]:.2f} minutes")
plt.show()