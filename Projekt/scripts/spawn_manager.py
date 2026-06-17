"""Spawn manager.

Provides a small utility to determine a player spawn from a TMX (Tiled) file
without requiring extra libraries. Falls back to sensible defaults.
"""
from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from typing import Optional, Tuple, Type


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

        return entity_cls(*point)

