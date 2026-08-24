# py -m pip install pygame-ce PyOpenGL numpy pytest
# Run: python main.py
"""
3D Top-Down Zombie Looter Shooter
"""
import pygame as pg
import settings
from entities.player import Player
from systems.camera_system import Camera
from pygame.locals import DOUBLEBUF, OPENGL
import sys, math, random, ctypes
import numpy as np
from pygame import mixer
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
from systems.input_system import poll_input

SCREEN_W, SCREEN_H = 1200, 800
FPS = 120
WORLD_HALF = 50.0

class RenderSystem:
    def init_opengl(self, width: int, height: int) -> None:
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-WORLD_HALF, WORLD_HALF, WORLD_HALF, -WORLD_HALF, -1, 1)
        glMatrixMode(GL_MODELVIEW)

    def begin_frame(self) -> None:
        glClearColor(0.08, 0.1, 0.12, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

    def draw_ground(self) -> None:
        glColor3f(0.18, 0.28, 0.2)
        glBegin(GL_QUADS)
        glVertex2f(-WORLD_HALF, -WORLD_HALF)
        glVertex2f(WORLD_HALF, -WORLD_HALF)
        glVertex2f(WORLD_HALF, WORLD_HALF)
        glVertex2f(-WORLD_HALF, WORLD_HALF)
        glEnd()

    def draw_player(self, player: Player) -> None:
        radius = settings.PLAYER_RADIUS
        glColor3f(0.9, 0.75, 0.2)
        glBegin(GL_QUADS)
        glVertex2f(player.x - radius, player.z - radius)
        glVertex2f(player.x + radius, player.z - radius)
        glVertex2f(player.x + radius, player.z + radius)
        glVertex2f(player.x - radius, player.z + radius)
        glEnd()

    def end_frame(self) -> None:
        pg.display.flip()

render_system = RenderSystem()

def main() -> None:
    pg.init()
    pg.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), DOUBLEBUF | OPENGL)
    render_system.init_opengl(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    player = Player(0, 0)
    camera = Camera(player)
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
            render_system.draw_player(player)
            render_system.end_frame()
    pg.quit()

if __name__ == "__main__":
    main()