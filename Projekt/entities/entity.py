
from __future__ import annotations

import numpy as np


class Entity:
    def __init__(self, position=(0.0, 0.0, 0.0), radius: float = 0.5) -> None:
        self.position = np.asarray(position, dtype=float).copy()
        self.radius = float(radius)

    @property
    def x(self) -> float:
        return float(self.position[0])

    @property
    def y(self) -> float:
        return float(self.position[1])

    @property
    def z(self) -> float:
        return float(self.position[2])
