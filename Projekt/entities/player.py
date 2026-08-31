"""Spielerentitaet mit einfacher WASD- und Pfeiltastenbewegung."""

import math

import pygame as pg

import settings
from entities.entity import Entity


class Player(Entity):
    def __init__(self, x: float = 0.0, z: float = 0.0, radius: float = 0.5) -> None:
        super().__init__(position=(float(x), 0.5, float(z)), radius=radius)

    @property
    def x(self) -> float:
        return float(self.position[0])

    @x.setter
    def x(self, value):
        self.position[0] = float(value)

    @property
    def z(self) -> float:
        return float(self.position[2])

    @z.setter
    def z(self, value):
        self.position[2] = float(value)

    def update(self, dt: float, input_state: dict) -> None:
        keys = input_state["keys"]

        def pressed(key: int) -> bool:
            return bool(keys.get(key, False)) if hasattr(keys, "get") else bool(keys[key])

        move_x = float(pressed(pg.K_d) or pressed(pg.K_RIGHT)) - float(
            pressed(pg.K_a) or pressed(pg.K_LEFT)
        )
        move_z = float(pressed(pg.K_s) or pressed(pg.K_DOWN)) - float(
            pressed(pg.K_w) or pressed(pg.K_UP)
        )

        length = math.hypot(move_x, move_z)
        if length > 0.0:
            self.x += move_x / length * settings.PLAYER_SPEED * dt
            self.z += move_z / length * settings.PLAYER_SPEED * dt