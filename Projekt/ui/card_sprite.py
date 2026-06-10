import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class CardSprite:

    WIDTH = 100
    HEIGHT = 140

    def __init__(self, card, x, y):
        self.card = card
        self.x = x
        self.y = y

    def draw(self, screen, font):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.WIDTH, self.HEIGHT))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.WIDTH, self.HEIGHT), 2)
        txt = font.render(f"{self.card.value}", True, BLACK)
        suit = font.render(self.card.suit[0], True, BLACK)
        screen.blit(txt, (self.x + 10, self.y + 10))
        screen.blit(suit, (self.x + 10, self.y + 50))
