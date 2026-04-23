import pygame as pg
import json
import random
import networkx as nx

WIDTH, HEIGHT = 900, 650
FPS = 60

SOURCE = "s"
SINK = "t"

SPEED_SCALE = 0.25  # smaller = slower cars
NUM_CARS = 20

# ---------------- EDGE ----------------
class Edge:
    def __init__(self, u, v, capacity):
        self.u = u
        self.v = v
        self.capacity = capacity
        self.flow = 0

    def latency(self):
        eps = 1e-3
        return 1.0 / (self.capacity - self.flow + eps)

# ---------------- CAR ----------------
class Car:
    def __init__(self, start):
        self.current = start
        self.next = None
        self.progress = 0.0
        self.edge = None
        self.done = False

    def choose_next(self, graph):
        outgoing = graph.outgoing[self.current]

        if not outgoing:
            self.done = True
            return

        # GREEDY LOGIC: 
        # Evaluate all outgoing edges and pick the one with the MINIMUM latency
        # We still check if the edge moves us toward the sink to avoid loops
        valid_edges = [
            e for e in outgoing 
            if graph.dist_to_sink.get(e.v, float('inf')) <= graph.dist_to_sink.get(self.current, float('inf'))
        ]

        if not valid_edges:
            self.done = True
            return

        # Sort by latency and pick the best (greedy)
        self.edge = min(valid_edges, key=lambda e: e.latency())
        
        self.next = self.edge.v
        self.edge.flow += 1
        self.progress = 0.0

    def update(self, graph, dt):
        if self.done:
            return

        # If no edge yet, choose one
        if self.edge is None:
            self.choose_next(graph)
            return

        # Move along edge
        speed = SPEED_SCALE / self.edge.latency()
        self.progress += speed * dt

        # Handle reaching end of edge
        if self.progress >= 1.0:
            # Clamp (prevents overshoot bugs)
            self.progress = 1.0

            # Leave current edge
            self.edge.flow -= 1

            # Move to next node
            self.current = self.next

            # If reached sink, stop
            if self.current == SINK:
                self.done = True
                self.edge = None
                return

            # IMPORTANT: reset BEFORE picking next edge
            self.edge = None
            self.next = None
            self.progress = 0.0

            # Now choose next edge cleanly
            self.choose_next(graph)
            
# ---------------- GRAPH ----------------
class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.outgoing = {}
        self.dist_to_sink = {}

    def add_node(self, name, pos):
        self.nodes[name] = pos
        self.outgoing[name] = []

    def add_edge(self, u, v, capacity):
        e = Edge(u, v, capacity)
        self.edges.append(e)
        self.outgoing[u].append(e)

# ---------------- LOAD GRAPH ----------------
def load_graph(filename):
    with open(filename) as f:
        data = json.load(f)

    g = Graph()

    for name, pos in data["nodes"].items():
        g.add_node(name, tuple(pos))

    for e in data["edges"]:
        g.add_edge(e["u"], e["v"], e["capacity"])

    return g

# ---------------- DISTANCE TO SINK ----------------
def compute_dist_to_sink(graph):
    G = nx.DiGraph()

    # reverse edges
    for e in graph.edges:
        G.add_edge(e.v, e.u, weight=1)

    return nx.single_source_dijkstra_path_length(G, SINK)

# ---------------- DRAW ----------------
def draw(graph, cars, screen, font):
    screen.fill((25, 25, 30))

    # draw edges
    for e in graph.edges:
        p1 = graph.nodes[e.u]
        p2 = graph.nodes[e.v]

        ratio = min(1.0, e.flow / e.capacity)
        color = (int(255 * ratio), 120, 120)
        width = int(2 + 8 * ratio)

        pg.draw.line(screen, color, p1, p2, width)

        # label
        mid = ((p1[0]+p2[0])//2, (p1[1]+p2[1])//2)
        eq = "1/(c-f)"
        val = f"{e.latency():.2f}"

        text = font.render(f"{eq}={val}", True, (255,255,255))
        screen.blit(text, mid)

    # draw cars
    for car in cars:
        if car.edge is None:
            continue

        p1 = graph.nodes[car.edge.u]
        p2 = graph.nodes[car.edge.v]

        x = p1[0] + (p2[0] - p1[0]) * car.progress
        y = p1[1] + (p2[1] - p1[1]) * car.progress

        pg.draw.circle(screen, (80, 200, 255), (int(x), int(y)), 4)

    # draw nodes
    for name, pos in graph.nodes.items():
        pg.draw.circle(screen, (220, 220, 220), pos, 12)
        label = font.render(name, True, (0, 0, 0))
        screen.blit(label, (pos[0]-6, pos[1]-10))

    # UI
    txt = font.render(f"Cars: {len(cars)}", True, (255,255,255))
    screen.blit(txt, (10, 10))

# ---------------- MAIN ----------------
def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    font = pg.font.SysFont(None, 22)

    graph = load_graph("graph.json")
    graph.dist_to_sink = compute_dist_to_sink(graph)

    cars = []
    spawn_rate = 12  # more cars
    spawn_timer = 0

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        # spawn cars
        spawn_timer += dt
        while spawn_timer > 1.0 / spawn_rate and len(cars) < NUM_CARS:
            spawn_timer -= 1.0 / spawn_rate
            cars.append(Car(SOURCE))

        # update cars
        for car in cars:
            car.update(graph, dt)

        cars = [c for c in cars if not c.done]

        draw(graph, cars, screen, font)
        pg.display.flip()

    pg.quit()

if __name__ == "__main__":
    main()