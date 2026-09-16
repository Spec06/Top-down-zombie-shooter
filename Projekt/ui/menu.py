"""Menu implementation with keyboard navigation."""

from __future__ import annotations

try:
    import pygame
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

