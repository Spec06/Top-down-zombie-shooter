"""Enemy entity scaffold."""

import numpy as np


class Enemy:
    def __init__(self, x=0.0, z=0.0):
        # Position as 3D numpy array for compatibility with the 3D main loop
        # Use a fixed Y (height) so enemy sits on the ground similar to Player
        self.position = np.array([float(x), 0.5, float(z)], dtype=float)
        self.components = {}
        self.alive = True

    def add_component(self, name, comp):
        self.components[name] = comp

    def get(self, name):
        return self.components.get(name)

    def is_dead(self):
        h = self.get('health')
        if h:
            return h.is_dead()
        return not self.alive

