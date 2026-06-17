"""3D game entry using Pygame + PyOpenGL.

Refurbished from `game.py` to run as `Projekt/main.py`.
Controls: W/A/S/D move, Left/Right rotate, ESC to quit.
"""
import math
import numpy as np
import pygame as pg
from pygame.locals import DOUBLEBUF, OPENGL, K_w, K_s, K_a, K_d, K_LEFT, K_RIGHT, K_ESCAPE
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective, gluLookAt

# Settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
PLAYER_SPEED = 5.0


class Player:
    def __init__(self, x=0.0, z=0.0):
        self.position = np.array([x, 0.5, z], dtype=float)
        self.rotation = 0.0
        self.mesh_size = 0.5

    def update(self, dt):
        keys = pg.key.get_pressed()
        rot_rad = math.radians(self.rotation)
        forward = np.array([math.sin(rot_rad), 0.0, -math.cos(rot_rad)])
        right = np.array([math.cos(rot_rad), 0.0, math.sin(rot_rad)])

        movement = np.array([0.0, 0.0, 0.0])
        if keys[K_w]:
            movement += forward
        if keys[K_s]:
            movement -= forward
        if keys[K_a]:
            movement -= right
        if keys[K_d]:
            movement += right

        if np.linalg.norm(movement) > 0:
            movement = movement / np.linalg.norm(movement)
            self.position += movement * PLAYER_SPEED * dt

    def rotate(self, dt):
        keys = pg.key.get_pressed()
        rotation_speed = 150.0 * dt
        if keys[K_LEFT]:
            self.rotation -= rotation_speed
        if keys[K_RIGHT]:
            self.rotation += rotation_speed


class Camera:
    def __init__(self, target, distance=8.0, pitch=30.0):
        self.target = np.array(target, dtype=float)
        self.distance = distance
        self.pitch = pitch
        self.yaw = 0.0

    def update(self, player: Player):
        self.target = np.array([player.position[0], player.position[1], player.position[2]])
        self.yaw = player.rotation

    def apply(self):
        pitch_rad = math.radians(self.pitch)
        yaw_rad = math.radians(self.yaw)
        d = self.distance
        cam_x = self.target[0] + d * math.cos(pitch_rad) * math.sin(yaw_rad)
        cam_y = self.target[1] + d * math.sin(pitch_rad)
        cam_z = self.target[2] + d * math.cos(pitch_rad) * math.cos(yaw_rad)

        glLoadIdentity()
        gluLookAt(cam_x, cam_y, cam_z, self.target[0], self.target[1], self.target[2], 0, 1, 0)


def draw_cube(size=1.0):
    hs = size / 2.0
    verts = [
        (-hs, -hs,  hs), ( hs, -hs,  hs), ( hs,  hs,  hs), (-hs,  hs,  hs),
        (-hs, -hs, -hs), ( hs, -hs, -hs), ( hs,  hs, -hs), (-hs,  hs, -hs)
    ]
    faces = [
        (0,1,2,3), (4,5,6,7), (3,2,6,7), (0,1,5,4), (1,2,6,5), (0,3,7,4)
    ]
    colors = [(1,0,0),(0,1,0),(0,0,1),(1,1,0),(0.5,0.5,0.5),(0.8,0,0.8)]

    glBegin(GL_QUADS)
    for fi, face in enumerate(faces):
        glColor3fv(colors[fi % len(colors)])
        for vi in face:
            glVertex3fv(verts[vi])
    glEnd()


def init_opengl(width, height):
    glViewport(0, 0, width, height)
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.5, 0.7, 1.0, 1.0)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (1.0, 1.0, 1.0, 0.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(width)/float(height), 0.1, 200.0)
    glMatrixMode(GL_MODELVIEW)


def game_loop():
    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)
    pg.display.set_caption("Top-Down Looter Shooter [3D]")

    init_opengl(SCREEN_WIDTH, SCREEN_HEIGHT)

    player = Player(0.0, 0.0)
    camera = Camera(player.position, distance=12.0, pitch=30.0)

    clock = pg.time.Clock()
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

        # Update
        player.rotate(dt)
        player.update(dt)
        camera.update(player)

        # Render
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        camera.apply()

        # Draw ground as large scaled cube (flat)
        glPushMatrix()
        glTranslatef(0.0, -1.0, 0.0)
        glScalef(30.0, 0.1, 30.0)
        draw_cube(1.0)
        glPopMatrix()

        # Draw player
        glPushMatrix()
        glTranslatef(player.position[0], player.position[1], player.position[2])
        glRotatef(player.rotation, 0, 1, 0)
        draw_cube(player.mesh_size)
        glPopMatrix()

        pg.display.flip()

    pg.quit()


if __name__ == '__main__':
    print('Starting 3D game (Pygame + PyOpenGL)')
    game_loop()