import pygame

class Button:

def __init__(self, x, y, w, h, text):

    self.rect = pygame.Rect(x, y, w, h)
    self.text = text

def draw(self, screen, font):

    pygame.draw.rect(
        screen,
        (220,220,220),
        self.rect
    )

    pygame.draw.rect(
        screen,
        (0,0,0),
        self.rect,
        2
    )

    txt = font.render(
        self.text,
        True,
        (0,0,0)
    )

    screen.blit(
        txt,
        txt.get_rect(
            center=self.rect.center
        )
    )

def is_clicked(self, pos):
    return self.rect.collidepoint(pos)