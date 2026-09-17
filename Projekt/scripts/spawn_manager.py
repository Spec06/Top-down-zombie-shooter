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
    from Projekt.components.health import Health
except ImportError:  # pragma: no cover - legacy local layout
    from components.health import Health


class SpawnManager:
    """Create enemy or player instances at map-relative coordinates."""

    @staticmethod
    def _create_entity(entity_cls: Type, x: float, z: float, zombie_type: str = "normal"):
        """Instantiate entities across different constructor signatures."""
        try:
            return entity_cls(x, z, zombie_type=zombie_type)
        except TypeError:
            try:
                return entity_cls(x, z, ztype=zombie_type)
            except TypeError:
                return entity_cls(x, z)

    def spawn_enemy(
        self,
        entity_cls: Type,
        x: float,
        z: float,
        zombie_type: str = "normal",
        max_health: Optional[float] = None,
    ):
        """Create one enemy and attach its health component when supported."""
        enemy = self._create_entity(entity_cls, x, z, zombie_type)
        if hasattr(enemy, "add_component"):
            maximum_health = max_health or getattr(enemy, "max_hp", None)
            if maximum_health is None:
                stats = getattr(enemy, "stats", {})
                maximum_health = stats.get("hp", 10)
            enemy.add_component("health", Health(max_hp=maximum_health))
        return enemy

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
            enemy = self.spawn_enemy(
                entity_cls,
                x,
                z,
                zombie_type,
                max_health=hp if zombie_types is None else None,
            )

            enemies.append(enemy)

        return enemies

    def spawn_wave(self, entity_cls: Type, player_pos, wave: int = 1, radius_min: float = 22.0, radius_max: float = 30.0, zombie_types=None):
        """Compatibility helper matching the legacy wave spawning pattern."""
        px, _, pz = player_pos
        enemies = []
        while len(enemies) < max(1, wave):
            angle = random.uniform(0, math.tau)
            dist = random.uniform(radius_min, radius_max)
            x = px + math.cos(angle) * dist
            z = pz + math.sin(angle) * dist
            zombie_type = random.choice(zombie_types) if zombie_types else "normal"
            enemy = self.spawn_enemy(entity_cls, x, z, zombie_type)
            enemies.append(enemy)
        return enemies

