"""Procedural arena construction for the game world."""

from __future__ import annotations

import math
import random


class WorldBuilder:
    """Build obstacles and boundary walls for a playable arena."""

    def __init__(self, world_half: float) -> None:
        self.world_half = float(world_half)

    def build_arena(self, obstacle_count: int = 25) -> tuple[list[dict], list[dict]]:
        obstacles = []
        for _ in range(obstacle_count):
            x = random.uniform(-self.world_half * 0.85, self.world_half * 0.85)
            z = random.uniform(-self.world_half * 0.85, self.world_half * 0.85)
            if math.hypot(x, z) < 10:
                continue
            obstacles.append(
                {
                    "x": x,
                    "z": z,
                    "w": random.uniform(2, 5),
                    "d": random.uniform(2, 5),
                    "h": random.uniform(2, 6),
                }
            )

        thickness = 1.0
        boundary = self.world_half
        walls = [
            {"x": 0, "z": boundary + thickness / 2, "w": boundary * 2 + thickness * 2, "d": thickness, "h": 3},
            {"x": 0, "z": -boundary - thickness / 2, "w": boundary * 2 + thickness * 2, "d": thickness, "h": 3},
            {"x": boundary + thickness / 2, "z": 0, "w": thickness, "d": boundary * 2 + thickness * 2, "h": 3},
            {"x": -boundary - thickness / 2, "z": 0, "w": thickness, "d": boundary * 2 + thickness * 2, "h": 3},
        ]
        return obstacles, walls