"""Top-down game main entry with a simple Pygame menu and demo loop."""
import sys
import math
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_SPEED

from ui.menu import Menu
from entities.player import Player
from components.movement import Movement
from systems.input_system import InputSystem
from scripts.spawn_manager import SpawnManager


def run_game_loop(screen):
    """A minimal demo game loop with WASD control.

    Creates a player entity (spawn from TMX if available) and allows movement
    with WASD. Returns when ESC is pressed or window closed.
    """
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 24)

    # spawn player (try TMX spawn, fallback to center)
    sm = SpawnManager()
    player = sm.spawn(Player, tmx_path='Projekt/maps/level_1.tmx')
    # attach movement component
    mv = Movement(speed=PLAYER_SPEED)
    player.add_component('movement', mv)

    input_system = InputSystem()
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
        # use InputSystem to update movement velocities
        input_system.update([player])

        # update position
        x, y = player.position
        vx, vy = mv.velocity
        player.position = (x + vx * dt, y + vy * dt)

        # draw
        screen.fill((12, 34, 48))
        # draw player as a circle
        px, py = int(player.position[0]), int(player.position[1])
        pygame.draw.circle(screen, (200, 80, 80), (px, py), 12)

        info = font.render("WASD to move — ESC to return", True, (240, 240, 240))
        screen.blit(info, (10, 10))
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