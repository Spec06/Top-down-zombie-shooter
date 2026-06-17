"""Top-down game main entry with a simple Pygame menu and demo loop."""
import sys
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

from ui.menu import Menu


def run_game_loop(screen):
    """A minimal demo game loop that returns when ESC is pressed."""
    clock = pygame.time.Clock()
    running = True
    font = pygame.font.SysFont("arial", 24)
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        screen.fill((12, 34, 48))
        text = font.render("Game running - press ESC to return to menu", True, (240, 240, 240))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text, rect)
        pygame.display.flip()

    return True


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Top-Down Game")

    def start_cb():
        ok = run_game_loop(screen)
        return ok

    def options_cb():
        print("Options selected (not implemented)")
        return None

    def quit_cb():
        pygame.quit()
        sys.exit(0)

    menu = Menu(["Start Game", "Options", "Quit"], title="Top-Down Game", callbacks=[start_cb, options_cb, quit_cb])

    # Run menu in a blocking way until user selects Quit (quit_cb will sys.exit)
    try:
        selection = menu.run_pygame_blocking(screen)
        print("Menu selection returned:", selection)
    except SystemExit:
        return


if __name__ == "__main__":
    main()