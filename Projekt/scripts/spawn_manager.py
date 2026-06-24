"""Spawn manager.

Provides a small utility to determine a player spawn from a TMX (Tiled) file
without requiring extra libraries. Falls back to sensible defaults.
"""
from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from typing import Optional, Tuple, Type, List
import random
import math

# Import components used for spawned entities
try:
    from components.health import Health
except Exception:
    # if running as script from root, try the other import path
    from Projekt.components.health import Health


class SpawnManager:
    def __init__(self):
        self.spawn_points = []

    def get_player_spawn(self, tmx_path: str) -> Optional[Tuple[float, float]]:
        """Try to read a `player_spawn` object from the TMX file.

        Returns (x, y) in pixels, or None if not found / file missing.
        Uses ElementTree so no external dependency is required.
        """
        if not tmx_path or not os.path.isfile(tmx_path):
            return None
        try:
            tree = ET.parse(tmx_path)
            root = tree.getroot()

            # Search for any <object name="player_spawn" .../>
            for obj in root.findall('.//object'):
                if obj.get('name') == 'player_spawn':
                    x = float(obj.get('x', '0'))
                    y = float(obj.get('y', '0'))
                    return (x, y)

            # If no object found, try to compute center from map attributes
            width = int(root.get('width') or 0)
            height = int(root.get('height') or 0)
            tilewidth = int(root.get('tilewidth') or 0)
            tileheight = int(root.get('tileheight') or 0)
            if width and height and tilewidth and tileheight:
                return (width * tilewidth / 2.0, height * tileheight / 2.0)
        except Exception:
            return None
        return None

    def spawn(self, entity_cls: Type, point: Optional[Tuple[float, float]] = None, tmx_path: Optional[str] = None):
        """Instantiate `entity_cls` at `point`. If `point` is None, try TMX then fallbacks.

        Example:
            sm = SpawnManager()
            player = sm.spawn(Player, tmx_path='Projekt/maps/level_1.tmx')
        """
        if point is None:
            point = None
            if tmx_path:
                point = self.get_player_spawn(tmx_path)
            if point is None:
                # fallback to settings center if available
                try:
                    from settings import SCREEN_WIDTH, SCREEN_HEIGHT

                    point = (SCREEN_WIDTH / 2.0, SCREEN_HEIGHT / 2.0)
                except Exception:
                    point = (0.0, 0.0)

        # Many entity constructors in this project expect (x, z) like Player(x, z)
        # so pass two arguments. If entity_cls accepts different signature it
        # should handle missing z internally.
        return entity_cls(point[0], point[1])

    def spawn_enemies(self, entity_cls: Type, count: int = 3, center: Optional[Tuple[float, float]] = None,
                      radius: float = 5.0, tmx_path: Optional[str] = None, hp: int = 10) -> List:
        """Spawn multiple enemies around `center` (or TMX player spawn / fallback).

        - `entity_cls` is the enemy class to instantiate (expects x,z)
        - `count` number of enemies
        - `center` tuple (x, y) in map coordinates; note: TMX y maps to z in 3D world
        - `radius` spawn radius around center
        - `hp` initial health for each enemy
        Returns a list of created enemy instances.
        """
        if center is None:
            center = self.get_player_spawn(tmx_path) or (0.0, 0.0)

        enemies = []
        cx, cy = float(center[0]), float(center[1])
        for i in range(count):
            angle = random.random() * math.tau
            r = random.random() * radius
            sx = cx + math.cos(angle) * r
            sy = cy + math.sin(angle) * r
            e = self.spawn(entity_cls, point=(sx, sy), tmx_path=tmx_path)
            # attach Health component if available
            try:
                e.add_component('health', Health(max_hp=hp))
            except Exception:
                pass
            # attach Movement component if available (for knockback)
            try:
                from components.movement import Movement
                e.add_component('movement', Movement(speed=2.5))
            except Exception:
                try:
                    from Projekt.components.movement import Movement
                    e.add_component('movement', Movement(speed=2.5))
                except Exception:
                    pass
            enemies.append(e)

        return enemies

