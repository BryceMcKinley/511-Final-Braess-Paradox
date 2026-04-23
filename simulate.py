
import swarmanoid as sw
import occupancygrid as og
import pygame as pg
import numpy as np 


WORLD_SIZE = 1000
ROBOT_RADIUS = 10

pg.init()
screen = pg.display.set_mode((WORLD_SIZE, WORLD_SIZE))
pg.display.set_caption("Robot Simulation")

def draw_robot(surface, robot):
    x, y = robot.location
    color = sw.get_color(robot.color)

    if isinstance(robot, sw.Eyebot):
        # Circle
        pg.draw.circle(surface, color, (int(x), int(y)), ROBOT_RADIUS)

    elif isinstance(robot, sw.Handbot):
        # Square
        pg.draw.rect(
            surface,
            color,
            (int(x - ROBOT_RADIUS),
             int(y - ROBOT_RADIUS),
             ROBOT_RADIUS * 2,
             ROBOT_RADIUS * 2)
        )

    elif isinstance(robot, sw.Footbot):
        # Triangle
        points = [
            (x, y - ROBOT_RADIUS),
            (x - ROBOT_RADIUS, y + ROBOT_RADIUS),
            (x + ROBOT_RADIUS, y + ROBOT_RADIUS),
        ]
        pg.draw.polygon(surface, color, points)

def simulate(swarm, grid):
    clock = pg.time.Clock()
    running = True

    while running:
        screen.fill((30, 30, 30))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        # Draw grid FIRST (background)
        grid.draw(screen)

        # Draw robots
        for robot in swarm.robots:
            draw_robot(screen, robot)

        pg.display.flip()
        clock.tick(60)

    pg.quit()


if __name__ == "__main__":
    swarm = sw.swarmanoid()
    swarm.add_robot(sw.Eyebot(1, (100, 100)))
    swarm.add_robot(sw.Footbot(2, (300, 200)))
    swarm.add_robot(sw.Handbot(3, (500, 400)))

    grid = og.OccupancyGrid(WORLD_SIZE, cell_size=30)

    simulate(swarm, grid)