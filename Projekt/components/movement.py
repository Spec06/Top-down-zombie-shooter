"""Movement component (velocity-based)."""

class Movement:
    def __init__(self, speed=100):
        self.speed = speed
        self.velocity = (0, 0)

    def set_velocity(self, vx, vy):
        self.velocity = (vx, vy)
