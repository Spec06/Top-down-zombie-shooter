"""Spawn manager.

Provides simple spawn helpers for the top-down zombie shooter.
"""
from __future__ import annotations

import math
import os
import random
import xml.etree.ElementTree as ET
from typing import List, Optional, Tuple, Type

try:
    from components.health import Health
except ImportError:  # pragma: no cover
    from Projekt.components.health import Health


class SpawnManager:
    """Create enemy or player instances at map-relative coordinates."""

    def __init__(self, fallback_center: Optional[Tuple[float, float]] = None) -> None:
        self.fallback_center = fallback_center or (0.0, 0.0)

    @staticmethod
    def _read_tmx_spawn(tmx_path: str) -> Optional[Tuple[float, float]]:
        if not tmx_path or not os.path.isfile(tmx_path):
            return None

        try:
            root = ET.parse(tmx_path).getroot()
            for obj in root.findall('.//object'):
                if obj.get('name') == 'player_spawn':
                    return float(obj.get('x', 0)), float(obj.get('y', 0))

            width = int(root.get('width', 0) or 0)
            height = int(root.get('height', 0) or 0)
            tile_width = int(root.get('tilewidth', 0) or 0)
            tile_height = int(root.get('tileheight', 0) or 0)
            if width and height and tile_width and tile_height:
                return width * tile_width / 2.0, height * tile_height / 2.0
        except Exception:
            return None
        return None

    def spawn(self, entity_cls: Type, point: Optional[Tuple[float, float]] = None, tmx_path: Optional[str] = None):
        if point is None:
            point = self._read_tmx_spawn(tmx_path) if tmx_path else None
        if point is None:
            point = self.fallback_center
        return entity_cls(point[0], point[1])

    def spawn_enemies(
        self,
        entity_cls: Type,
        count: int = 3,
        center: Optional[Tuple[float, float]] = None,
        radius: float = 5.0,
        tmx_path: Optional[str] = None,
        hp: int = 10,
        zombie_types=None,
    ) -> List:
        if center is None:
            center = self._read_tmx_spawn(tmx_path) if tmx_path else self.fallback_center

        cx, cy = float(center[0]), float(center[1])
        enemies: List = []

        for _ in range(max(0, count)):
            angle = random.random() * math.tau
            distance = random.random() * max(0.0, radius)
            x = cx + math.cos(angle) * distance
            z = cy + math.sin(angle) * distance
            zombie_type = random.choice(zombie_types) if zombie_types else "normal"
            enemy = entity_cls(x, z, zombie_type=zombie_type)

            try:
                enemy.add_component('health', Health(max_hp=enemy.stats["hp"] if zombie_types else hp))
            except AttributeError:
                pass

            enemies.append(enemy)

        return enemies

