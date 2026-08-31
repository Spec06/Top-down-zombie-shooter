"""Enemy entity scaffold."""

from entities.entity import Entity


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

    def add_component(self, name, comp):
        self.components[name] = comp

    def get(self, name):
        return self.components.get(name)

    def is_dead(self):
        h = self.get('health')
        if h:
            return h.is_dead()
        return not self.alive

