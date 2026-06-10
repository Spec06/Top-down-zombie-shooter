import pygame

GREEN = (0,120,0)
WHITE = (255,255,255)
BLACK = (0,0,0)

class PokerTable:

    def draw(
        self,
        screen,
        font,
        game
    ):

        screen.fill(GREEN)

        pygame.draw.ellipse(
            screen,
            (0,90,0),
            (150,80,950,500)
        )

        pygame.draw.ellipse(
            screen,
            BLACK,
            (150,80,950,500),
            5
        )

        pot_text = font.render(
            f"Pot: {game.pot}",
            True,
            WHITE
        )

        screen.blit(
            pot_text,
            (560,250)
        )

        player_text = font.render(
            f"Du: {game.player.chips}",
            True,
            WHITE
        )

        ai_text = font.render(
            f"Computer: {game.ai.chips}",
            True,
            WHITE
        )

        screen.blit(player_text, (50,650))
        screen.blit(ai_text, (50,20))