
import numpy as np

from Projekt.components.health import Health
from Projekt.systems.render_system import mat4_mul, mat4_rotate_x, mat4_scale, mat4_translate

try:
    from Projekt.entities.entity import Entity
    from Projekt.entities.player import Player
    from Projekt import settings
except ModuleNotFoundError:  # pragma: no cover - legacy local layout
    from entities.entity import Entity
    from entities.player import Player
    import settings


ZOMBIE_TYPES = {
    "normal": {"hp": 50, "speed": 2.5, "damage": 10, "attack_cooldown": 1.0, "color": (0.4, 0.5, 0.2), "size": (0.6, 1.6, 0.6)},
    "fast": {"hp": 25, "speed": 5.0, "damage": 7, "attack_cooldown": 1.0, "color": (0.6, 0.4, 0.2), "size": (0.4, 1.4, 0.4)},
    "tank": {"hp": 100, "speed": 1.3, "damage": 20, "attack_cooldown": 1.0, "color": (0.3, 0.3, 0.2), "size": (1.0, 2.2, 1.0)},
}


class Enemy(Entity):
    def __init__(self, x=0.0, z=0.0, radius: float = 0.5, zombie_type: str = "normal", ztype: str | None = None):
        super().__init__(position=(float(x), 0.5, float(z)), radius=radius)
        self.components = {}
        self.alive = True
        selected_type = ztype if ztype is not None else zombie_type
        self.zombie_type = selected_type if selected_type in ZOMBIE_TYPES else "normal"
        self.stats = ZOMBIE_TYPES[self.zombie_type]
        self.size = self.stats["size"]
        self.health = Health(self.stats["hp"])
        self.add_component("health", self.health)
        self.attack_timer = 0.0
        self.dying = False
        self.dying_time = 0.0
        self.dying_duration = 0.8
        self.dead = False
        self.hit_flash = 0.0
        self.wobble = 0.0

    @property
    def ztype(self) -> str:
        return self.zombie_type

    @property
    def hp(self) -> float:
        return self.health.current

    @property
    def max_hp(self) -> float:
        return self.health.max_hp

    @property
    def pos(self):
        return self.position

    def take_damage(self, amount: float) -> bool:
        if self.dying or self.is_dead():
            return False
        self.health.take_damage(amount)
        self.alive = not self.health.is_dead()
        self.hit_flash = 0.15
        if not self.alive:
            self.dying = True
        return True

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

    def update(self, dt: float, game) -> None:
        self.attack_timer = max(0.0, self.attack_timer - dt)
        if self.dying:
            self.dying_time += dt
            if self.dying_time >= self.dying_duration:
                self.dead = True
                game.on_zombie_killed(self)
            return

        direction = np.asarray(game.player.position - self.position, dtype=float)
        distance = float(np.linalg.norm(direction))
        if distance > 1.25:
            direction = direction / distance
            self.wobble += dt * 4.0
            perpendicular = np.array([-direction[2], 0, direction[0]])
            direction += perpendicular * (np.sin(self.wobble) * 0.15)
            direction /= max(np.linalg.norm(direction), 1e-6)
            new_x = self.x + direction[0] * self.stats["speed"] * dt
            new_z = self.z + direction[2] * self.stats["speed"] * dt
            half_size = max(self.size[0], self.size[2]) / 2
            if not game.is_position_blocked(new_x, self.z, half_size):
                self.x = new_x
            if not game.is_position_blocked(self.x, new_z, half_size):
                self.z = new_z

        if distance < 1.5 and self.can_attack():
            game.player.take_damage(self.stats["damage"], game)
        self.hit_flash = max(0.0, self.hit_flash - dt)

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
        return self.health.is_dead() or not self.alive

    def draw(self, renderer) -> None:
        sx, sy, sz = self.size
        flash = self.hit_flash / 0.15 if self.hit_flash > 0 else 0
        emissive = (flash, 0, 0)
        if self.dying:
            progress = self.dying_time / self.dying_duration
            model = mat4_mul(
                mat4_mul(
                    mat4_mul(mat4_translate(self.x, -progress * 0.5 + sy / 2, self.z), mat4_rotate_x(progress * (np.pi / 2))),
                    mat4_scale(sx, sy, sz),
                ),
                mat4_translate(0, -0.5, 0),
            )
            renderer.draw_cube(model, self.stats["color"], emissive=emissive, alpha=max(0, 1 - progress * 0.5))
            return
        renderer.draw_cube(mat4_mul(mat4_translate(self.x, sy / 2, self.z), mat4_scale(sx, sy, sz)), self.stats["color"], emissive=emissive)
        renderer.draw_cube(mat4_mul(mat4_translate(self.x, sy + 0.15, self.z), mat4_scale(sx * 0.6, 0.3, sz * 0.6)), tuple(min(1.0, channel * 1.2) for channel in self.stats["color"]))

