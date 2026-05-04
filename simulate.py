import random
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from dataclasses import dataclass

@dataclass
class SimulationParams:
    INCLUDE_SHORTCUT: bool = True
    NUM_CARS: int = 4000
    ITERATIONS: int = 60
    ALTRUISTIC_PERCENTAGE: float = 0.0
    RNDM_SWITCH: bool = False
    DELETE_SHORTCUT_HALF_WAY: bool = False
    APPLY_TOLL_HALF_WAY: bool = False
    TOLL_VALUE: int = 0
    RNDM_SWITCH_PROB: float = 0.05
    LEARNING_RATE_OVERRIDE: float = 0.0
    # DATA_DELAY: 0 means real-time info; > 0 uses history from N steps ago
    DATA_DELAY: int = 0 

class City:
    def __init__(self, name, pos):
        self.name = name
        self.pos = pos
        self.out_roads = []

    def connect(self, road):
        self.out_roads.append(road)

class Road:
    def __init__(self, start, end, road_type, toll=0):
        self.start = start
        self.end = end
        self.road_type = road_type
        self.cars = 0
        self.toll = toll
        start.connect(self)

    def travel_time(self):
        base_time = 0
        if self.road_type == "bottleneck": 
            base_time = self.cars / 100
        elif self.road_type == "highway": 
            base_time = 45
        elif self.road_type == "shortcut": 
            base_time = 0 + self.toll
        elif self.road_type == "broken": 
            base_time = 200
        return base_time

    def get_label(self):
        t = self.travel_time()
        label = f"{self.road_type}\nTime: {t:.1f}\nCars: {self.cars}"
        if self.toll > 0: 
            label += f"\nToll: {self.toll}"
        return label

class Simulation:
    def __init__(self, params: SimulationParams):
        self.params = params
        
        # Determine initial Learning Rate
        if self.params.LEARNING_RATE_OVERRIDE > 0:
            self.learning_rate = self.params.LEARNING_RATE_OVERRIDE
        else:
            self.learning_rate = 0.2
            
        self.step_count = 0
        self.it_car_speeds = []
        self.path_time_history = [] # For DATA_DELAY tracking
        
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
        
        if self.params.INCLUDE_SHORTCUT:
            self.roads.append(Road(self.A, self.B, "shortcut", toll=self.params.TOLL_VALUE))
            
        self.car_paths = [random.choice(self.get_available_paths()) for _ in range(self.params.NUM_CARS)]
        self.pos = {city.name: city.pos for city in [self.S, self.A, self.B, self.T]}

    def get_available_paths(self):
        paths = [[self.roads[0], self.roads[2]], [self.roads[1], self.roads[3]]]
        if len(self.roads) > 4:
            paths.append([self.roads[0], self.roads[4], self.roads[3]])
        return paths

    def step(self):
        # Handle mid-simulation logic
        if self.params.DELETE_SHORTCUT_HALF_WAY and self.step_count == self.params.ITERATIONS // 2:
            if len(self.roads) > 4: 
                self.roads[4].road_type = "broken"
                    
        if self.params.APPLY_TOLL_HALF_WAY and self.step_count == self.params.ITERATIONS // 2:
            if len(self.roads) > 4 and self.roads[4].road_type != "broken":
                self.roads[4].toll = self.params.TOLL_VALUE 

        # Update current traffic load
        for r in self.roads: r.cars = 0
        for path in self.car_paths:
            for road in path: 
                road.cars += 1
        
        # Log real-time data
        available_paths = self.get_available_paths()
        current_real_times = [sum(r.travel_time() for r in p) for p in available_paths]
        self.path_time_history.append(current_real_times)

        # Apply Data Delay logic
        if self.params.DATA_DELAY > 0 and len(self.path_time_history) > self.params.DATA_DELAY:
            perceived_times = self.path_time_history[-(self.params.DATA_DELAY + 1)]
        else:
            perceived_times = current_real_times

        best_path_idx = np.argmin(perceived_times)
        best_path = available_paths[best_path_idx]
        
        car_speeds = [sum(r.travel_time() for r in p) for p in self.car_paths]

        actual_travel_times = [sum(r.travel_time() for r in p) for p in self.car_paths]
        avg_experienced_time = sum(actual_travel_times) / self.params.NUM_CARS

        # Dynamic Learning Rate (skipped if override is active)
        if self.params.LEARNING_RATE_OVERRIDE == 0:
            std = np.std(car_speeds)
            if std * 0.1 < self.learning_rate:
                self.learning_rate = max(0.1, std * 0.1 - (self.step_count/self.params.ITERATIONS) * 0.0001)
        
        if self.step_count == 0:
            self.it_car_speeds = list(car_speeds)

        # Update Car Decisions
        for i in range(self.params.NUM_CARS):
            # Rule 1: Learning
            if random.random() < self.learning_rate:
                self.car_paths[i] = best_path
            
            # Rule 2: Random Switching (Frustration)
            if self.params.RNDM_SWITCH and car_speeds[i] > self.it_car_speeds[i]:
                if random.random() < self.params.RNDM_SWITCH_PROB:
                    alt = [x for x in available_paths if x != self.car_paths[i]]
                    self.car_paths[i] = random.choice(alt)
            
            # Rule 3: Altruism
            if random.random() < self.params.ALTRUISTIC_PERCENTAGE:
                self.car_paths[i] = random.choice([available_paths[0], available_paths[1]])

        self.step_count += 1
        return avg_experienced_time
    
    def draw_network(self, i, avg_time):
        plt.subplot(1, 2, 1)
        plt.cla()
        G = nx.DiGraph()
        edge_labels = {(r.start.name, r.end.name): r.get_label() for r in self.roads}
        for r in self.roads: 
            G.add_edge(r.start.name, r.end.name)
        
        nx.draw(G, self.pos, with_labels=True, node_size=1000, node_color='orange', 
                font_weight='bold', arrows=True, connectionstyle='arc3, rad = 0.1')
        nx.draw_networkx_edge_labels(G, self.pos, edge_labels=edge_labels, font_size=15)
        plt.title(f"Traffic Network (Iter {i})")