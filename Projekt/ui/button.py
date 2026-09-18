import pygame


class Button:
    def __init__(self, x, y, w, h, text, callback=None, *, fg=(0, 0, 0), bg=(220, 220, 220), hover_bg=(255, 200, 50), border=2):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = str(text)
        self.callback = callback
        self.fg = fg
        self.bg = bg
        self.hover_bg = hover_bg
        self.border = border
        self.hover = False
        self.pressed = False

    def handle_event(self, event):
        """Handle a pygame event. Call this from your main event loop."""
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.pressed = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.pressed:
                self.pressed = False
                if self.rect.collidepoint(event.pos):
                    if callable(self.callback):
                        try:
                            return self.callback()
                        except Exception:
                            return None
        return None

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, screen, font=None):
        """Draw the button. Provide a Pygame `screen` and optional `font`."""
        if font is None:
            font = pygame.font.SysFont("arial", 20)

        color = self.hover_bg if self.hover else self.bg
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, self.border)

        txt_surf = font.render(self.text, True, self.fg)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        screen.blit(txt_surf, txt_rect)
