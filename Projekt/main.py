# py -m pip install pygame-ce PyOpenGL numpy pytest
# Run: python main.py
"""
3D Top-Down Zombie Looter Shooter
"""
import pygame as pg
import settings
from components.health import Health
from entities.player import Player
from entities.projectile import Projectile
from entities.enemy import Enemy
from systems.camera_system import Camera
from systems.render_system import Render_system
from systems.combat_system import CombatSystem
from pygame.locals import DOUBLEBUF, OPENGL
import sys, math, random, ctypes
import numpy as np
from pygame import mixer
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective
from OpenGL.GL.shaders import compileShader, compileProgram
from systems.input_system import poll_input

SCREEN_W, SCREEN_H = 1200, 800
FPS = 120
WORLD_HALF = 50.0

def main() -> None:
    pg.init()
    pg.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), DOUBLEBUF | OPENGL)
    Render_system.init_opengl(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    player = Player(0, 0)
    camera = Camera(player)
    enemy = Enemy(5, 5, 0.5)
    enemy.add_component('health', Health(max_hp=10))
    render_system = Render_system
    combat_system = CombatSystem(world=[enemy])
    projectiles: list[Projectile] = []
    clock = pg.time.Clock()
    running = True
    while running:
        dt = clock.tick(settings.FPS) / 1000.0
        input_state = poll_input()
        running = not input_state["quit"]
        if running:
            player.update(dt, input_state)
            if any(
                event.type == pg.KEYDOWN and event.key == pg.K_SPACE
                for event in input_state["events"]
            ):
                projectiles.append(
                    Projectile((player.x, 0.5, player.z), (0.0, 0.0, -1.0))
                )
            for projectile in projectiles:
                projectile.update(dt)
            projectiles = [projectile for projectile in projectiles if projectile.is_alive()]
            camera.update(player)
            render_system.begin_frame()
            camera.apply()
            render_system.draw_ground()
            render_system.draw_cube(
                (player.x, 0.5, player.z),
                1.0,
                (0.2, 0.7, 1.0),
            )
            for projectile in projectiles:
                render_system.draw_cube(projectile.position, 0.2, (1.0, 0.8, 0.1))
            if not enemy.is_dead():
                render_system.draw_cube(
                    (enemy.x, 0.5, enemy.z),
                    1.0,
                    (1.2, 1.7, 1.0),
                )
                enemy.update(dt, player)
            render_system.end_frame()
            projectiles = combat_system.handle_projectiles(projectiles, [enemy])
    pg.quit()

if __name__ == "__main__":
    main()