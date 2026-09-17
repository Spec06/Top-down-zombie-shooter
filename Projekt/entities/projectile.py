from collections.abc import Sequence

import numpy as np

from Projekt import settings

try:
    from Projekt.entities.entity import Entity
except ModuleNotFoundError:  # pragma: no cover - legacy local layout
    from entities.entity import Entity

from Projekt.systems.render_system import mat4_rotate_y, mat4_scale, mat4_translate, mat4_mul


class Projectile(Entity):
    """Projectile entity used by both tests and the game loop."""

    def __init__(
        self,
        start_pos: Sequence[float],
        direction: Sequence[float],
        speed: float = 20.0,
        lifetime: float = 5.0,
        radius: float = 0.2,
        damage: float = 1.0,
        color=(1.0, 1.0, 1.0),
        owner: str = "player",
    ) -> None:
        super().__init__(position=start_pos, radius=radius)
        direction_vector = np.asarray(direction, dtype=float)
        direction_length = np.linalg.norm(direction_vector)
        if direction_length == 0.0:
            raise ValueError("Projectile direction must not be zero")
        self.velocity = direction_vector / direction_length * speed
        self.lifetime = float(lifetime)
        self._age = 0.0
        self.damage = damage
        self.color = color
        self.owner = owner
        self.dead = False

    @property
    def pos(self):
        return self.position

    @property
    def vel(self):
        return self.velocity

    def update(self, dt: float, game=None) -> None:
        self.position = self.position + self.velocity * dt
        self._age += dt
        if self._age >= self.lifetime:
            self.dead = True

        if game is None or self.dead:
            return
        world_half = getattr(game, "world_half", settings.WORLD_HALF)
        if abs(self.position[0]) > world_half or abs(self.position[2]) > world_half:
            self.dead = True
            return
        if game.is_position_blocked(self.position[0], self.position[2], self.radius):
            self.dead = True
            return
        for enemy in game.zombies:
            if enemy.dying:
                continue
            if abs(self.position[0] - enemy.pos[0]) < enemy.size[0] / 2 + self.radius:
                if abs(self.position[2] - enemy.pos[2]) < enemy.size[2] / 2 + self.radius:
                    if enemy.take_damage(self.damage):
                        game.add_feedback(str(int(self.damage)), enemy.pos[:], (1, 0.2, 0.2), vy=2.0)
                        game.play_sound("hit")
                    self.dead = True
                    return

    def is_alive(self) -> bool:
        return not self.dead and self._age < self.lifetime

    def draw(self, renderer) -> None:
        model = mat4_mul(
            mat4_translate(self.position[0], self.position[1], self.position[2]),
            mat4_scale(0.12, 0.12, 0.3),
        )
        model = mat4_mul(model, mat4_rotate_y(np.arctan2(self.velocity[2], self.velocity[0])))
        renderer.draw_cube(model, self.color, emissive=(0.6, 0.5, 0.2))
