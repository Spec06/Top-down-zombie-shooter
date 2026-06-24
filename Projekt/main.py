"""3D game entry using Pygame + PyOpenGL.

Refurbished from `game.py` to run as `Projekt/main.py`.
Controls: W/A/S/D move, Left/Right rotate, ESC to quit.
"""
import math
import numpy as np
import pygame as pg
from pygame.locals import DOUBLEBUF, OPENGL, K_w, K_s, K_a, K_d, K_LEFT, K_RIGHT, K_ESCAPE
import settings

# import unified Player entity
from entities.player import Player
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective, gluLookAt

# Game systems / components
from components.attack import Attack
from components.health import Health
from components.effects import FlashEffect
from systems.combat_system import CombatSystem
from entities.enemy import Enemy
from scripts.spawn_manager import SpawnManager
from systems.particle_system import ParticleSystem

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


def draw_solid_cube(size=1.0, color=(1.0, 1.0, 1.0, 1.0)):
    """Draw a uniformly colored cube (uses current model transform)."""
    hs = size / 2.0
    verts = [
        (-hs, -hs,  hs), ( hs, -hs,  hs), ( hs,  hs,  hs), (-hs,  hs,  hs),
        (-hs, -hs, -hs), ( hs, -hs, -hs), ( hs,  hs, -hs), (-hs,  hs, -hs)
    ]
    faces = [
        (0,1,2,3), (4,5,6,7), (3,2,6,7), (0,1,5,4), (1,2,6,5), (0,3,7,4)
    ]
    r, g, b, a = color
    glColor4f(r, g, b, a)
    glBegin(GL_QUADS)
    for face in faces:
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


def draw_debug_circle(center_xz, radius, y=0.5, segments=48):
    """Draw a thin circle (line loop) in the XZ plane at height y."""
    cx, cz = float(center_xz[0]), float(center_xz[1])
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 0.2, 0.2)
    glBegin(GL_LINE_LOOP)
    for i in range(segments):
        theta = 2.0 * math.pi * float(i) / float(segments)
        x = cx + radius * math.cos(theta)
        z = cz + radius * math.sin(theta)
        glVertex3f(x, y + 0.01, z)
    glEnd()
    glEnable(GL_LIGHTING)


def game_loop():
    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)
    pg.display.set_caption("Top-Down Looter Shooter [3D]")

    init_opengl(SCREEN_WIDTH, SCREEN_HEIGHT)

    player = Player(0.0, 0.0)
    camera = Camera(player.position, distance=12.0, pitch=30.0)

    # debug draw flag
    debug_draw = bool(getattr(settings, 'DEBUG_DRAW_HITBOX', False))

    # --- Minimal combat setup ---
    # Player attack component (melee)
    attack_comp = Attack(damage=3, range=2.5, cooldown=0.6)

    # Spawn multiple enemies around the player using SpawnManager
    sm = SpawnManager()
    # Use player's x,z as center for spawns
    center = (player.position[0], player.position[2])
    enemies = sm.spawn_enemies(Enemy, count=3, center=center, radius=6.0, hp=8)

    combat = CombatSystem(world=enemies)
    particles = ParticleSystem()

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
                if event.key == pg.K_F1:
                    debug_draw = not debug_draw
                # Attack on SPACE
                if event.key == pg.K_SPACE:
                    hits = combat.perform_melee(player, attack_comp)
                    if hits:
                        for h in hits:
                            hh = h.get('health')
                            if hh:
                                print(f"Hit {h} -> HP now {hh.current}/{hh.max}")
                            # add flash effect component
                            try:
                                h.add_component('flash', FlashEffect(duration=0.25))
                            except Exception:
                                pass
                            # spawn particles at target position
                            try:
                                particles.spawn_hit(h.position, count=10, spread=1.2)
                            except Exception:
                                pass
                            if h.is_dead():
                                print(f"Enemy died: {h}")
                                try:
                                    enemies.remove(h)
                                except ValueError:
                                    pass
                        # refresh world reference inside combat system
                        combat.world = enemies

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

        # Debug: draw attack range circle on XZ plane
        if debug_draw:
            try:
                # draw circle centered on player at ground level
                draw_debug_circle((player.position[0], player.position[2]), attack_comp.range, y=player.position[1])
            except Exception:
                pass

        # Draw enemies (apply flash if present)
        for e in list(enemies):
            glPushMatrix()
            glTranslatef(e.position[0], e.position[1], e.position[2])
            # check for flash component
            flash = e.get('flash')
            if flash:
                try:
                    # draw a bright overlay cube while flash is active
                    if flash.is_active():
                        # slightly larger overlay
                        glPushMatrix()
                        glScalef(1.05, 1.05, 1.05)
                        glEnable(GL_BLEND)
                        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                        # draw a solid white cube overlay with alpha
                        draw_solid_cube(e.mesh_size if hasattr(e, 'mesh_size') else 0.5, color=(1.0, 1.0, 1.0, 0.9))
                        glDisable(GL_BLEND)
                        glPopMatrix()
                    # update flash timer
                    flash.update(dt)
                except Exception:
                    pass

            # default draw of enemy cube
            glRotatef(0, 0, 1, 0)
            # use standard draw
            draw_cube(0.5)
            glPopMatrix()

        # update and draw particles
        particles.update(dt)
        particles.draw()

        pg.display.flip()

    pg.quit()


if __name__ == '__main__':
    print('Starting 3D game (Pygame + PyOpenGL)')
    game_loop()