"""HUD overlay showing important player stats."""

from __future__ import annotations

try:
    import pygame
    from OpenGL.GL import GL_LINES, GL_QUADS, GL_RGBA, GL_UNSIGNED_BYTE, GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER, GL_LINEAR, glBegin, glBindTexture, glColor3f, glDeleteTextures, glDisable, glEnable, glEnd, glGenTextures, glLineWidth, glTexCoord2f, glTexImage2D, glTexParameteri, glVertex2f
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

    def draw(self, screen, entity, weapon_name="pistol", magazine=0, reserve=0, mouse_pos=(0, 0)) -> None:
        """Render stats and crosshair as a screen-space OpenGL overlay."""
        if pygame is None:
            return
        current, maximum = self._resolve_health(entity)
        width, height = screen.get_size()
        from OpenGL.GL import GL_PROJECTION, GL_MODELVIEW, glLoadIdentity, glMatrixMode, glOrtho, glDisable, glEnable, GL_DEPTH_TEST
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPush = __import__("OpenGL.GL", fromlist=["glPushMatrix"]).glPushMatrix
        glPop = __import__("OpenGL.GL", fromlist=["glPopMatrix"]).glPopMatrix
        glPush()
        glLoadIdentity()
        glOrtho(0, width, height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPush()
        glLoadIdentity()

        def bar(y, value, maximum, color):
            ratio = max(0.0, min(1.0, value / max(1.0, maximum)))
            glColor3f(0.08, 0.08, 0.08)
            glBegin(GL_QUADS)
            glVertex2f(20, y)
            glVertex2f(270, y)
            glVertex2f(270, y + 18)
            glVertex2f(20, y + 18)
            glColor3f(*color)
            glVertex2f(20, y)
            glVertex2f(20 + 250 * ratio, y)
            glVertex2f(20 + 250 * ratio, y + 18)
            glVertex2f(20, y + 18)
            glEnd()

        bar(20, current, maximum, (0.8, 0.12, 0.12))
        bar(44, entity.stamina, entity.max_stamina, (0.15, 0.65, 0.95))
        glColor3f(1.0, 0.85, 0.2)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        x, y = mouse_pos
        glVertex2f(x - 10, y)
        glVertex2f(x + 10, y)
        glVertex2f(x, y - 10)
        glVertex2f(x, y + 10)
        glEnd()
        if self.font is None:
            self.font = pygame.font.SysFont(self.font_name, self.font_size)
        hint = self.font.render(
            f"HP {current}/{maximum}   STAMINA {int(entity.stamina)}   {weapon_name.upper()} {magazine}/{reserve}   |   WASD Move  SHIFT Sprint  LMB Fire  R Reload  1-3 Weapons",
            True,
            (235, 235, 235),
        )
        texture = glGenTextures(1)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, hint.get_width(), hint.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, pygame.image.tostring(hint, "RGBA", False))
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(20, 92)
        glTexCoord2f(1.0, 0.0)
        glVertex2f(20 + hint.get_width(), 92)
        glTexCoord2f(1.0, 1.0)
        glVertex2f(20 + hint.get_width(), 92 + hint.get_height())
        glTexCoord2f(0.0, 1.0)
        glVertex2f(20, 92 + hint.get_height())
        glEnd()
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)
        glDeleteTextures([texture])
        glPop()
        glMatrixMode(GL_PROJECTION)
        glPop()
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)
