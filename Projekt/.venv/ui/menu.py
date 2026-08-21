"""Menu implementation with optional Pygame support.

This `Menu` supports keyboard navigation and simple rendering via Pygame
if `pygame` is available. It also provides a minimal console fallback.
"""
try:
    import pygame
    PYGAME_AVAILABLE = True
except Exception:
    PYGAME_AVAILABLE = False


class Menu:
    def __init__(self, items, title=None, callbacks=None):
        """Create a menu.

        - `items`: list of strings
        - `title`: optional title string
        - `callbacks`: optional list of callables for each item
        """
        self.items = list(items)
        self.title = title
        self.selected = 0
        self.callbacks = callbacks or [None] * len(self.items)

    def move_up(self):
        self.selected = (self.selected - 1) % len(self.items)

    def move_down(self):
        self.selected = (self.selected + 1) % len(self.items)

    def select(self):
        cb = None
        if 0 <= self.selected < len(self.callbacks):
            cb = self.callbacks[self.selected]
        if callable(cb):
            return cb()
        return self.selected

    def handle_key(self, key):
        if not PYGAME_AVAILABLE:
            return None
        if key == pygame.K_UP:
            self.move_up()
        elif key == pygame.K_DOWN:
            self.move_down()
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            return self.select()
        return None

    def draw_pygame(self, screen, font=None, title_font=None, fg=(255, 255, 255), sel_fg=(255, 200, 50)):
        """Draw the menu using a Pygame `screen` and optional `font`.

        Requires `PYGAME_AVAILABLE`.
        """
        if not PYGAME_AVAILABLE:
            raise RuntimeError("Pygame is not available")

        w, h = screen.get_size()
        if font is None:
            font = pygame.font.SysFont("arial", 24)
        if title_font is None:
            title_font = pygame.font.SysFont("arial", 36)

        screen.fill((30, 30, 30))

        y = 80
        if self.title:
            surf = title_font.render(self.title, True, fg)
            rect = surf.get_rect(center=(w // 2, y))
            screen.blit(surf, rect)
            y += 60

        for i, it in enumerate(self.items):
            color = sel_fg if i == self.selected else fg
            surf = font.render(it, True, color)
            rect = surf.get_rect(center=(w // 2, y))
            screen.blit(surf, rect)
            y += 40

    def run_pygame_blocking(self, screen, clock=None, font=None, title_font=None):
        """Run a blocking menu loop until an item is selected. Returns the selection result."""
        if not PYGAME_AVAILABLE:
            raise RuntimeError("Pygame is not available")
        import pygame as _pygame

        running = True
        if clock is None:
            clock = _pygame.time.Clock()

        while running:
            for event in _pygame.event.get():
                if event.type == _pygame.QUIT:
                    return None
                if event.type == _pygame.KEYDOWN:
                    res = self.handle_key(event.key)
                    if res is not None:
                        return res
            self.draw_pygame(screen, font=font, title_font=title_font)
            _pygame.display.flip()
            clock.tick(60)

    def open_console(self):
        """Simple console fallback for environments without Pygame."""
        print(self.title or "Menu")
        for i, it in enumerate(self.items):
            prefix = "> " if i == self.selected else "  "
            print(f"{prefix}{i+1}. {it}")
        try:
            choice = int(input("Choose (number): ")) - 1
            if 0 <= choice < len(self.items):
                self.selected = choice
                return self.select()
        except Exception:
            return None

