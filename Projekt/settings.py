"""Shared settings for the top-down game package."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_ROOT / "assets"

SCREEN_WIDTH: int = 1280
SCREEN_HEIGHT: int = 720
FPS: int = 60
PLAYER_SPEED: float = 5.0
PLAYER_RADIUS: float = 0.3
ENEMY_SPEED: float = 3.0
WORLD_HALF: float = 50.0
DEBUG_DRAW_HITBOX: bool = False
CAMERA_DISTANCE: float = 8.0
CAMERA_PITCH: float = 30.0