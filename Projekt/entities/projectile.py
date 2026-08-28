from collections.abc import Sequence

import numpy as np

class Projectile:
      def __init__(self, start_pos: Sequence[float], direction: Sequence[float], speed: float = 20.0, lifetime: float = 5.0,) -> None:
            self._pos = np.asarray(start_pos, dtype=float).copy()
            direction_vector = np.asarray(direction, dtype=float)
            direction_length = np.linalg.norm(direction_vector)
            if direction_length == 0.0:
                  raise ValueError("Projectile direction must not be zero")
            self.velocity = direction_vector / direction_length * speed
            self.lifetime = float(lifetime)
            self._age = 0.0

      def update(self, dt: float) -> None:
            self._pos += self.velocity * dt
            self._age += dt

      def is_alive(self) -> bool:
            return self._age < self.lifetime

      @property
      def position(self) -> np.ndarray:
            return self._pos.copy()