import pygame
import asyncio

from settings import WIDTH, HEIGHT, FPS, GREEN
from logic.gamemanager import GameManager
from ui.button import Button
from ui.table import PokerTable
from ui.card_sprite import CardSprite

pygame.init()

screen = pygame.display.set_mode(
(WIDTH, HEIGHT)
)

clock = pygame.time.Clock()
async def main():
    font = pygame.font.SysFont(
    "arial",
    28
    )

    game = GameManager()
    game.new_round()

    table = PokerTable()

    check_btn = Button(
    50, 630, 150, 50, "Check"
    )

    call_btn = Button(
    230, 630, 150, 50, "Call"
    )

    raise_btn = Button(
    410, 630, 150, 50, "Raise"
    )

    fold_btn = Button(
    590, 630, 150, 50, "Fold"
    )

    running = True

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if check_btn.is_clicked(event.pos):
                    print("Check")

                if call_btn.is_clicked(event.pos):
                    print("Call")

                if raise_btn.is_clicked(event.pos):
                    print("Raise")

                if fold_btn.is_clicked(event.pos):
                    print("Fold")

        # draw table and game state
        table.draw(screen, font, game)

        # draw table cards
        for i, c in enumerate(game.table_cards):
            x = 440 + i * 110
            y = 260
            CardSprite(c, x, y).draw(screen, font)

        # draw player cards (bottom)
        for i, c in enumerate(game.player.hand):
            x = 540 + i * 110
            y = 520
            CardSprite(c, x, y).draw(screen, font)

        # draw AI cards (top) - show for now
        for i, c in enumerate(game.ai.hand):
            x = 540 + i * 110
            y = 120
            CardSprite(c, x, y).draw(screen, font)

        check_btn.draw(screen, font)
        call_btn.draw(screen, font)
        raise_btn.draw(screen, font)
        fold_btn.draw(screen, font)

        pygame.display.flip()
    await asyncio.sleep(0)
    pygame.quit()