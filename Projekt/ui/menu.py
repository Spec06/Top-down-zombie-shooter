
from __future__ import annotations

try:
    import pygame
    from OpenGL.GL import (
        GL_BLEND,
        GL_LINES,
        GL_QUADS,
        GL_PROJECTION,
        GL_MODELVIEW,
        GL_TEXTURE_2D,
        GL_RGBA,
        GL_UNSIGNED_BYTE,
        GL_TEXTURE_MIN_FILTER,
        GL_TEXTURE_MAG_FILTER,
        GL_LINEAR,
        glBegin,
        glBlendFunc,
        glColor3f,
        glDisable,
        glEnable,
        glEnd,
        glBindTexture,
        glDeleteTextures,
        glGenTextures,
        glLoadIdentity,
        glMatrixMode,
        glOrtho,
        glPopMatrix,
        glPushMatrix,
        glTexCoord2f,
        glTexImage2D,
        glTexParameteri,
        glVertex2f,
    )
except Exception:  # pragma: no cover
    pygame = None


class Menu:
    """Simple selectable menu with console fallback."""

    def __init__(self, items=None, title: str = "Menu", callbacks=None) -> None:
        self.items = list(items or [])
        self.title = title
        self.selected = 0
        self.callbacks = callbacks or [None] * len(self.items)

    def move_up(self) -> None:
        if not self.items:
            return
        self.selected = (self.selected - 1) % len(self.items)

    def move_down(self) -> None:
        if not self.items:
            return
        self.selected = (self.selected + 1) % len(self.items)

    def select(self):
        if not self.items:
            return None
        callback = self.callbacks[self.selected] if self.selected < len(self.callbacks) else None
        if callable(callback):
            return callback()
        return self.selected

    def handle_input(self, input_state) -> str:
        """Handle a simple input_state dict and return a mode."""
        keys = input_state.get('keys', {}) if isinstance(input_state, dict) else {}

        def pressed(key: int) -> bool:
            try:
                return bool(keys[key])
            except (IndexError, KeyError, TypeError):
                return bool(keys.get(key, False)) if hasattr(keys, 'get') else False

        if pygame is not None:
            if pressed(pygame.K_UP):
                self.move_up()
                return 'none'
            if pressed(pygame.K_DOWN):
                self.move_down()
                return 'none'
            if pressed(pygame.K_RETURN) or pressed(pygame.K_SPACE):
                return 'start'
            if pressed(pygame.K_ESCAPE):
                return 'quit'

        return 'none'

    def show(self, screen) -> None:
        """Render the menu to a pygame screen if available."""
        if pygame is None or screen is None:
            return None

        font = pygame.font.SysFont('arial', 24)
        title_font = pygame.font.SysFont('arial', 36)
        w, h = screen.get_size()
        screen.fill((30, 30, 30))
        y = 80

        if self.title:
            surface = title_font.render(self.title, True, (255, 255, 255))
            rect = surface.get_rect(center=(w // 2, y))
            screen.blit(surface, rect)
            y += 60

        for index, item in enumerate(self.items):
            color = (255, 200, 50) if index == self.selected else (255, 255, 255)
            surface = font.render(str(item), True, color)
            rect = surface.get_rect(center=(w // 2, y))
            screen.blit(surface, rect)
            y += 40

        pygame.display.flip()
        return None

    def draw_opengl(self, screen) -> None:
        """Render the menu inside an OpenGL window."""
        if pygame is None or screen is None:
            return

        width, height = screen.get_size()
        font = pygame.font.SysFont("arial", 24)
        title_font = pygame.font.SysFont("arial", 42, bold=True)
        small_font = pygame.font.SysFont("arial", 18)

        glDisable(0x0B71)  # GL_DEPTH_TEST, kept local to avoid another import path.
        glEnable(GL_BLEND)
        glBlendFunc(0x0302, 0x0303)  # SRC_ALPHA, ONE_MINUS_SRC_ALPHA
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, width, height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glColor3f(0.035, 0.045, 0.07)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(width, 0)
        glVertex2f(width, height)
        glVertex2f(0, height)
        glEnd()

        panel_left, panel_top = width * 0.28, height * 0.18
        panel_right, panel_bottom = width * 0.72, height * 0.82
        glColor3f(0.09, 0.12, 0.18)
        glBegin(GL_QUADS)
        glVertex2f(panel_left, panel_top)
        glVertex2f(panel_right, panel_top)
        glVertex2f(panel_right, panel_bottom)
        glVertex2f(panel_left, panel_bottom)
        glEnd()

        def text(surface, x, y):
            texture = glGenTextures(1)
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, texture)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                GL_RGBA,
                surface.get_width(),
                surface.get_height(),
                0,
                GL_RGBA,
                GL_UNSIGNED_BYTE,
                pygame.image.tostring(surface, "RGBA", False),
            )
            glColor3f(1.0, 1.0, 1.0)
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 0.0)
            glVertex2f(x, y)
            glTexCoord2f(1.0, 0.0)
            glVertex2f(x + surface.get_width(), y)
            glTexCoord2f(1.0, 1.0)
            glVertex2f(x + surface.get_width(), y + surface.get_height())
            glTexCoord2f(0.0, 1.0)
            glVertex2f(x, y + surface.get_height())
            glEnd()
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)
            glDeleteTextures([texture])

        title = title_font.render(self.title, True, (240, 245, 255))
        text(title, (width - title.get_width()) / 2, panel_top + 52)
        y = panel_top + 135
        for index, item in enumerate(self.items):
            selected = index == self.selected
            glColor3f(0.85, 0.55, 0.12) if selected else glColor3f(0.16, 0.2, 0.29)
            glBegin(GL_QUADS)
            glVertex2f(panel_left + 45, y - 10)
            glVertex2f(panel_right - 45, y - 10)
            glVertex2f(panel_right - 45, y + 38)
            glVertex2f(panel_left + 45, y + 38)
            glEnd()
            label = font.render(str(item), True, (255, 255, 255))
            text(label, (width - label.get_width()) / 2, y + 4)
            y += 68

        hint = small_font.render("Pfeile: Auswahl    Enter/Space: Bestatigen    ESC: Beenden", True, (180, 190, 205))
        text(hint, (width - hint.get_width()) / 2, panel_bottom - 42)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def open_console(self):
        """Fallback for terminals without pygame."""
        print(self.title or 'Menu')
        for index, item in enumerate(self.items):
            marker = '> ' if index == self.selected else '  '
            print(f'{marker}{index + 1}. {item}')
        try:
            choice = int(input('Choose (number): ')) - 1
            if 0 <= choice < len(self.items):
                self.selected = choice
                return self.select()
        except Exception:
            return None

