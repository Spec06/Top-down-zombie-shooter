"""Enemy entity scaffold."""

import numpy as np

try:
    from entities.entity import Entity
    from entities.player import Player
    import settings
except ModuleNotFoundError:  # package import
    from Projekt.entities.entity import Entity
    from Projekt.entities.player import Player
    from Projekt import settings


ZOMBIE_TYPES = {
    "normal": {"hp": 35, "speed": 3.0, "damage": 8.0, "attack_cooldown": 0.8, "color": (0.35, 0.5, 0.18), "scale": 1.0},
    "fast": {"hp": 22, "speed": 5.2, "damage": 5.0, "attack_cooldown": 0.45, "color": (0.8, 0.25, 0.12), "scale": 0.82},
    "tank": {"hp": 90, "speed": 1.65, "damage": 15.0, "attack_cooldown": 1.15, "color": (0.35, 0.2, 0.55), "scale": 1.3},
}


class Enemy(Entity):
    def __init__(self, x=0.0, z=0.0, radius: float = 0.5, zombie_type: str = "normal"):
        super().__init__(position=(float(x), 0.5, float(z)), radius=radius)
        self.components = {}
        self.alive = True
        self.zombie_type = zombie_type if zombie_type in ZOMBIE_TYPES else "normal"
        self.stats = ZOMBIE_TYPES[self.zombie_type]
        self.attack_timer = 0.0

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
        self.attack_timer = max(0.0, self.attack_timer - dt)
        direction = np.asarray(player.position - self.position, dtype=float)
        distance = float(np.linalg.norm(direction))
        if distance > 1.25:
            direction = direction / distance
            self.x += direction[0] * self.stats["speed"] * dt
            self.z += direction[2] * self.stats["speed"] * dt

    def can_attack(self) -> bool:
        if self.attack_timer > 0.0:
            return False
        self.attack_timer = self.stats["attack_cooldown"]
        return True

    def add_component(self, name, comp):
        self.components[name] = comp

    def get(self, name):
        return self.components.get(name)

    def is_dead(self):
        h = self.get('health')
        if h:
            return h.is_dead()
        return not self.alive

