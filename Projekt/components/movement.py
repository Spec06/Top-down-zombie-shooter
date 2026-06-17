"""Movement component (velocity-based)."""

class Movement:
    def __init__(self, speed=100):
        self.speed = speed
        self.velocity = (0, 0)

    def set_velocity(self, vx, vy):
        self.velocity = (vx, vy)

    def wasd(self, up=False, down=False, left=False, right=False):
        vx = 0
        vy = 0
        if up:
            vy -= self.speed
        if down:
            vy += self.speed
        if left:
            vx -= self.speed
        if right:
            vx += self.speed
        self.set_velocity(vx, vy)
