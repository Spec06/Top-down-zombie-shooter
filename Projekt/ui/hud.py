"""HUD overlay showing important player stats."""

from __future__ import annotations

try:
    import pygame
except Exception:  # pragma: no cover
    pygame = None


class HUD:
    """Simple heads-up display for player health and status."""

    def __init__(self, font_name: str = "arial", font_size: int = 18) -> None:
        self.font_name = font_name
        self.font_size = font_size
        self.font = None
        if pygame is not None:
            self.font = pygame.font.SysFont(font_name, font_size)

    def _resolve_health(self, entity) -> tuple[int, int]:
        health = getattr(entity, "health", None)
        if health is None:
            health = getattr(entity, "health_component", None)

        if health is None:
            return 0, 0

        current = getattr(health, "current", 0)
        maximum = getattr(health, "max_hp", current)
        return int(current), int(maximum)

    def draw(self, screen, entity) -> None:
        """Render the HUD onto a Pygame screen surface."""
        if pygame is None or screen is None:
            return

        if self.font is None:
            self.font = pygame.font.SysFont(self.font_name, self.font_size)

        current, maximum = self._resolve_health(entity)
        text = f"HP: {current}/{maximum}"
        label = self.font.render(text, True, (255, 255, 255))
        screen.blit(label, (20, 20))
        return label
