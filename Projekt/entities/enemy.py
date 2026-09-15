"""Enemy entity scaffold."""

import numpy as np

from entities.entity import Entity
from entities.player import Player
import settings


class Enemy(Entity):
    def __init__(self, x=0.0, z=0.0, radius: float = 0.5):
        super().__init__(position=(float(x), 0.5, float(z)), radius=radius)
        self.components = {}
        self.alive = True

    @property
    def x(self):
        return float(self.position[0])

    @x.setter
    def x(self, value):
        self.position[0] = float(value)

    @property
    def z(self):
        return float(self.position[2])

    @z.setter
    def z(self, value):
        self.position[2] = float(value)

    def update(self, dt: float, player: Player) -> None:
        direction = np.asarray(player.position - self.position, dtype=float)
        distance = float(np.linalg.norm(direction))
        if distance > 0.0:
            direction = direction / distance
            self.x += direction[0] * settings.ENEMY_SPEED * dt
            self.z += direction[2] * settings.ENEMY_SPEED * dt

    def add_component(self, name, comp):
        self.components[name] = comp

    def get(self, name):
        return self.components.get(name)

    def is_dead(self):
        h = self.get('health')
        if h:
            return h.is_dead()
        return not self.alive

