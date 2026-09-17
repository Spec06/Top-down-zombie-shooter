

from __future__ import annotations

import math
import random

import numpy as np

try:
    from Projekt.entities.entity import Entity
except ModuleNotFoundError:  # pragma: no cover - legacy local layout
    from entities.entity import Entity

from Projekt.systems.render_system import mat4_mul, mat4_scale, mat4_translate


LOOT_COLORS = {
    "ammo_pistol": (1, 1, 0),
    "ammo_shotgun": (1, 0.7, 0),
    "ammo_rifle": (0.7, 1, 0.3),
    "medkit": (1, 0.2, 0.2),
    "weapon_shotgun": (0.2, 0.5, 1),
    "weapon_rifle": (0.3, 0.7, 1),
}


class LootItem(Entity):
    def __init__(self, x: float, z: float, loot_type: str, amount: int = 1) -> None:
        super().__init__(position=(float(x), 0.25, float(z)), radius=0.28)
        self.loot_type = loot_type
        self.type = loot_type
        self.amount = amount
        self.color = LOOT_COLORS.get(loot_type, (1, 1, 1))
        self.bob = random.uniform(0, 2 * math.pi)
        self.picked = False
        self.life = 60.0

    @property
    def pos(self):
        return self.position

    def update(self, dt: float, game) -> None:
        self.bob += dt * 3.0
        self.life -= dt
        if self.life <= 0:
            self.picked = True
            return

        dx = game.player.pos[0] - self.pos[0]
        dz = game.player.pos[2] - self.pos[2]
        if dx * dx + dz * dz < 1.5 * 1.5:
            if game.player.pickup_loot(self, game):
                self.picked = True

    def draw(self, renderer) -> None:
        y = 0.3 + math.sin(self.bob) * 0.15
        emissive = tuple(channel * 0.5 for channel in self.color)
        model = mat4_mul(
            mat4_translate(self.pos[0], y, self.pos[2]),
            mat4_scale(0.4, 0.4, 0.4),
        )
        renderer.draw_cube(model, self.color, emissive=emissive)
        ring_model = mat4_mul(
            mat4_translate(self.pos[0], 0.02, self.pos[2]),
            mat4_scale(0.7, 1, 0.7),
        )
        renderer.draw_quad(ring_model, self.color, emissive=emissive, alpha=0.5)

    def collect(self, player, ammo: dict, magazine: dict, weapons: dict) -> bool:
        if self.loot_type == "medkit":
            health = getattr(player, "health", None)
            if health is None or health.current >= health.max_hp:
                return False
            health.heal(self.amount)
        elif self.loot_type == "stamina":
            player.stamina = min(player.max_stamina, player.stamina + self.amount)
        elif self.loot_type in ammo:
            ammo[self.loot_type] += self.amount
        elif self.loot_type in weapons:
            magazine[self.loot_type] = weapons[self.loot_type]["magazine"]
        else:
            return False
        return True