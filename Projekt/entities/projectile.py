from collections.abc import Sequence

import numpy as np

from entities.entity import Entity


class Projectile(Entity):
    def __init__(self, start_pos: Sequence[float], direction: Sequence[float], speed: float = 20.0, lifetime: float = 5.0, radius: float = 0.2) -> None:
        super().__init__(position=start_pos, radius=radius)
        direction_vector = np.asarray(direction, dtype=float)
        direction_length = np.linalg.norm(direction_vector)
        if direction_length == 0.0:
            raise ValueError("Projectile direction must not be zero")
        self.velocity = direction_vector / direction_length * speed
        self.lifetime = float(lifetime)
        self._age = 0.0
        self.damage = 1

    def update(self, dt: float) -> None:
        self.position = self.position + self.velocity * dt
        self._age += dt

    def is_alive(self) -> bool:
        return self._age < self.lifetime
