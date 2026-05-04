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




class City:
    def __init__(self, name, pos):
        self.name = name
        self.pos = pos
        self.out_roads = []

    def connect(self, road):
        self.out_roads.append(road)

class Road:
    def __init__(self, start, end, road_type, toll = 0):
        self.start = start
        self.end = end
        self.road_type = road_type
        self.cars = 0
        self.toll = toll 
        start.connect(self)

    def travel_time(self):
        base_time = 0
        if self.road_type == "bottleneck": base_time = self.cars / 100
        elif self.road_type == "highway": base_time = 45
        elif self.road_type == "shortcut": base_time = 0 + self.toll
        elif self.road_type == "broken": base_time = 200 
        return base_time

    def get_label(self):
        t = self.travel_time()
        label = f"{self.road_type}\nTime: {t:.1f}\nCars: {self.cars}"
        if self.toll > 0: label += f"\nToll: {self.toll}"
        return label

class Simulation:
    def __init__(self, params: SimulationParams):
        self.params = params        
        self.learning_rate = 0.2
        self.step_count = 0 # Start at 0
        self.it_car_speeds = []
        
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
        # Event Logic: Move outside the car loop so it only runs once per step[cite: 1]
        if self.params.DELETE_SHORTCUT_HALF_WAY and self.step_count == self.params.ITERATIONS // 2:
            if len(self.roads) > 4: self.roads[4].road_type = "broken"
                    
        # if APPLY_TOLL_HALF_WAY and self.step_count == ITERATIONS // 2:
        #     if len(self.roads) > 4 and self.roads[4].road_type != "broken":
        #         self.roads[4].toll = TOLL_VALUE 

        for r in self.roads: r.cars = 0
        for path in self.car_paths:
            for road in path: road.cars += 1
        
        available_paths = self.get_available_paths()
        path_times = [sum(r.travel_time() for r in p) for p in available_paths]
        best_path = available_paths[np.argmin(path_times)]
        
        car_speeds = [sum(r.travel_time() for r in p) for p in self.car_paths]
        std = np.std(car_speeds)
        if std * 0.1 < self.learning_rate:
            self.learning_rate = max(0.01, std * 0.1 - (self.step_count/self.params.ITERATIONS) * 0.0001)
        
        if self.step_count == 0:
            self.it_car_speeds = list(car_speeds)

        for i in range(self.params.NUM_CARS):
            if random.random() < self.learning_rate:
                self.car_paths[i] = best_path
            elif self.params.RNDM_SWITCH and car_speeds[i] > self.it_car_speeds[i]:
                if random.random() < self.params.RNDM_SWITCH_PROB:
                    alt = [x for x in available_paths if x != self.car_paths[i]]
                    self.car_paths[i] = random.choice(alt)
            
            # Using global altruism value[cite: 1]
            if random.random() < self.params.ALTRUISTIC_PERCENTAGE:
                self.car_paths[i] = random.choice([available_paths[0], available_paths[1]])

        self.step_count += 1
        total_time = sum(sum(r.travel_time() for r in p) for p in self.car_paths)
        return total_time / self.params.NUM_CARS
    
    def draw_network(self, i, avg_time):
        plt.subplot(1, 2, 1)
        plt.cla()
        G = nx.DiGraph()
        edge_labels = {(r.start.name, r.end.name): r.get_label() for r in self.roads}
        for r in self.roads: G.add_edge(r.start.name, r.end.name)
        
        nx.draw(G, self.pos, with_labels=True, node_size=1000, node_color='orange', 
                font_weight='bold', arrows=True, connectionstyle='arc3, rad = 0.1')
        nx.draw_networkx_edge_labels(G, self.pos, edge_labels=edge_labels, font_size=15)
        plt.title(f"Traffic Network (Iter {i})")