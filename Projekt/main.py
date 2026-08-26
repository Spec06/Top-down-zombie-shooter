# py -m pip install pygame-ce PyOpenGL numpy pytest
# Run: python main.py
"""
3D Top-Down Zombie Looter Shooter
"""
import pygame as pg
import settings
from entities.player import Player
from systems.camera_system import Camera
from systems.render_system import Render_system
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
    render_system = Render_system
    clock = pg.time.Clock()
    running = True
    while running:
        dt = clock.tick(settings.FPS) / 1000.0
        input_state = poll_input()
        running = not input_state["quit"]
        if running:
            player.update(dt, input_state)
            camera.update(player)
            render_system.begin_frame()
            camera.apply()
            render_system.draw_ground()
            render_system.draw_cube(
                (player.x, 0.5, player.z),
                1.0,
                (0.2, 0.7, 1.0),
            )
            render_system.end_frame()
    pg.quit()

if __name__ == "__main__":
    main()