"""Movement component (3D velocity-based) with knockback support."""

import numpy as np


class Movement:
    def __init__(self, speed: float = 5.0):
        # speed influences WASD-style movement magnitude
        self.speed = float(speed)
        # velocity as 3D numpy array [vx, vy, vz]
        self.velocity = np.array([0.0, 0.0, 0.0], dtype=float)

    def set_velocity(self, vx: float, vy: float, vz: float = 0.0):
        self.velocity = np.array([float(vx), float(vy), float(vz)], dtype=float)

    def wasd(self, forward: float = 0.0, right: float = 0.0):
        # forward and right are multipliers (-1..1)
        self.velocity = np.array([right * self.speed, 0.0, forward * self.speed], dtype=float)

    def apply_knockback(self, direction, strength: float):
        """Apply an instantaneous knockback in given `direction` (iterable x,z) with magnitude `strength`.

        direction is expected to be a 2D vector (dx, dz). The resulting velocity will be set on x and z.
        """
        try:
            dx, dz = float(direction[0]), float(direction[1])
        except Exception:
            return
        vec = np.array([dx, 0.0, dz], dtype=float)
        norm = np.linalg.norm(vec)
        if norm == 0:
            return
        vec = vec / norm
        self.velocity = vec * float(strength)
