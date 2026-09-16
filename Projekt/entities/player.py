"""Spielerentitaet mit einfacher WASD- und Pfeiltastenbewegung."""

import math

import pygame as pg

try:
    import settings
except ModuleNotFoundError:  # package import
    from Projekt import settings
try:
    from entities.entity import Entity
except ModuleNotFoundError:  # package import
    from Projekt.entities.entity import Entity


class Player(Entity):
    def __init__(self, x: float = 0.0, z: float = 0.0, radius: float = 0.5) -> None:
        super().__init__(position=(float(x), 0.5, float(z)), radius=radius)
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.aim_angle = 0.0

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
        sprinting = pressed(pg.K_LSHIFT) and length > 0.0 and self.stamina > 0.0
        speed = settings.PLAYER_SPEED * (1.8 if sprinting else 1.0)
        if sprinting:
            self.stamina = max(0.0, self.stamina - 32.0 * dt)
        else:
            self.stamina = min(self.max_stamina, self.stamina + 20.0 * dt)
        if length > 0.0:
            self.x += move_x / length * speed * dt
            self.z += move_z / length * speed * dt

        mouse_world = input_state.get("mouse_world")
        if mouse_world is not None:
            self.aim_angle = math.atan2(mouse_world[1] - self.z, mouse_world[0] - self.x)