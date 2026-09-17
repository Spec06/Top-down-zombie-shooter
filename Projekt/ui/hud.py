"""HUD overlay showing important player stats."""

from __future__ import annotations

import numpy as np

from Projekt.components.weapon import WEAPON_CONFIG

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


class GameHUD:
    """HUD used by the OpenGL game renderer."""

    def draw(self, renderer, text_renderer, game) -> None:
        renderer.begin_hud()
        player = game.player
        x, y, width, height = 20, game.screen_height - 50, 200, 20
        renderer.draw_hud_quad(x, y, width, height, (0.2, 0, 0))
        renderer.draw_hud_quad(x, y, width * player.hp / player.MAX_HP, height, (0.8, 0.1, 0.1))
        renderer.draw_text(text_renderer, "HP", x + 4, y, "small", (255, 255, 255))
        renderer.draw_text(text_renderer, f"{int(player.hp)}/{player.MAX_HP}", x + width - 75, y, "small", (255, 255, 255))

        stamina_y = y - 25
        renderer.draw_hud_quad(x, stamina_y, width, height, (0.2, 0.2, 0))
        renderer.draw_hud_quad(x, stamina_y, width * player.stamina / player.MAX_STAMINA, height, (0.9, 0.8, 0.1))
        renderer.draw_text(text_renderer, "STA", x + 5, stamina_y, "small", (255, 255, 255))

        weapon_y = stamina_y - 60
        weapon_key = player.current_weapon_key
        if weapon_key:
            weapon = WEAPON_CONFIG[weapon_key]
            renderer.draw_text(text_renderer, weapon["name"], x, weapon_y, "med", (255, 255, 255))
            renderer.draw_text(text_renderer, f"{player.magazine[weapon_key]} / {player.ammo[weapon_key]}", x, weapon_y + 28, "small", (255, 220, 100))
            if player.reloading:
                renderer.draw_text(text_renderer, "RELOADING...", x + 75, weapon_y, "med", (255, 100, 100))
        renderer.draw_text(text_renderer, f"Medkits: {player.consumables} (F)", x, weapon_y - 25, "small", (255, 100, 100))
        renderer.draw_text(text_renderer, f"Wave: {game.wave_mgr.wave}", 20, 20, "med", (255, 255, 255))
        renderer.draw_text(text_renderer, f"Zombies: {len(game.zombies)}", 20, 50, "small", (255, 100, 100))
        renderer.draw_text(text_renderer, f"Score: {game.score}", 20, 75, "small", (255, 220, 100))
        renderer.draw_text(text_renderer, f"Kills: {game.total_kills}", 20, 100, "small", (200, 200, 200))

        for index, weapon_key in enumerate(player.weapons):
            slot_x, slot_y = game.screen_width - 200 + index * 60, 20
            color = (0.3, 0.3, 0.3) if weapon_key is None else WEAPON_CONFIG[weapon_key]["color"]
            renderer.draw_hud_quad(slot_x, slot_y, 50, 50, (0.1, 0.1, 0.1))
            renderer.draw_hud_quad(slot_x + 4, slot_y + 4, 42, 42, color)
            if index == player.current_weapon:
                renderer.draw_hud_quad(slot_x - 2, slot_y - 2, 54, 54, (1, 1, 1), alpha=0.3)
            renderer.draw_text(text_renderer, str(index + 1), slot_x + 5, slot_y + 55, "small", (255, 255, 255))
            if weapon_key:
                renderer.draw_text(text_renderer, WEAPON_CONFIG[weapon_key]["name"][:3], slot_x + 5, slot_y + 5, "tiny", (255, 255, 255))

        if game.wave_mgr.between_waves:
            countdown = max(0, game.wave_mgr.countdown)
            label = f"Next Wave in {countdown:.1f}s" if game.wave_mgr.wave else f"First Wave in {countdown:.1f}s"
        else:
            label = f"Wave {game.wave_mgr.wave} - {len(game.zombies)} zombies left"
        renderer.draw_text(text_renderer, label, game.screen_width // 2, game.screen_height - 60, "med", (255, 255, 255), center=True)

        view_projection = np.dot(game.proj_matrix, game.view_matrix)
        for feedback in game.feedback_system:
            world = np.array([*feedback["pos"], 1], dtype=np.float32)
            clip = view_projection.dot(world)
            if clip[3] == 0:
                continue
            normalized = clip[:3] / clip[3]
            screen_x = (normalized[0] + 1) * 0.5 * game.screen_width
            screen_y = (1 - normalized[1]) * 0.5 * game.screen_height
            renderer.draw_text(
                text_renderer,
                feedback["text"],
                int(screen_x),
                int(screen_y),
                "small",
                feedback["color_rgb"],
                alpha=min(1.0, feedback["life"] * 2),
                center=True,
            )

        mouse_x, mouse_y = pygame.mouse.get_pos()
        renderer.draw_hud_quad(mouse_x - 1, mouse_y - 8, 2, 16, (1, 1, 1))
        renderer.draw_hud_quad(mouse_x - 8, mouse_y - 1, 16, 2, (1, 1, 1))
        renderer.end_hud()
