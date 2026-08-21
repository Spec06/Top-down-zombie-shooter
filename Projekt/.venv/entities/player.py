"""Player entity implementation compatible with 3D main loop."""

import numpy as np
import pygame as pg
import math


class Player:
    def __init__(self, x=0.0, z=0.0):
        # Position as 3D numpy array [x, y, z]
        self.position = np.array([float(x), 0.5, float(z)], dtype=float)
        self.rotation = 0.0
        self.mesh_size = 0.5
        self.components = {}

    def add_component(self, name, comp):
        self.components[name] = comp

    def get(self, name):
        return self.components.get(name)

    def update(self, dt, speed=5.0):
        keys = pg.key.get_pressed()
        rot_rad = math.radians(self.rotation)
        forward = np.array([math.sin(rot_rad), 0.0, -math.cos(rot_rad)])
        right = np.array([math.cos(rot_rad), 0.0, math.sin(rot_rad)])

        movement = np.array([0.0, 0.0, 0.0])
        if keys[pg.K_w]:
            movement += forward
        if keys[pg.K_s]:
            movement -= forward
        if keys[pg.K_a]:
            movement -= right
        if keys[pg.K_d]:
            movement += right

        if np.linalg.norm(movement) > 0:
            movement = movement / np.linalg.norm(movement)
            self.position += movement * float(speed) * float(dt)

    def rotate(self, dt, rotation_speed=150.0):
        keys = pg.key.get_pressed()
        rs = rotation_speed * dt
        if keys[pg.K_LEFT]:
            self.rotation -= rs
        if keys[pg.K_RIGHT]:
            self.rotation += rs
