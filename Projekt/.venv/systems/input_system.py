"""Sammelt Pygame-Eingaben und verarbeitet Bewegungskomponenten."""
import math
import pygame


def poll_input() -> dict:
    """Liest Events, Tastatur und Maus für den aktuellen Frame aus."""
    events = pygame.event.get()
    keys = pygame.key.get_pressed()
    mouse = {
        "pos": pygame.mouse.get_pos(),
        "buttons": pygame.mouse.get_pressed(3),
    }
    quit_requested = any(
        event.type == pygame.QUIT
        or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)
        for event in events
    )
    return {
        "quit": quit_requested,
        "keys": keys,
        "events": events,
        "mouse": mouse,
    }


class InputSystem:
    def __init__(self):
        pass

    def update(self, entities):
        """Read current keyboard state and set velocities on movement components.

        `entities` is an iterable of entity objects that have components accessible
        via `.get('movement')`.
        """
        keys = pygame.key.get_pressed()

        for e in entities:
            mv = e.get('movement')
            if not mv:
                continue

            dx = (1 if keys[pygame.K_d] else 0) - (1 if keys[pygame.K_a] else 0)
            dy = (1 if keys[pygame.K_s] else 0) - (1 if keys[pygame.K_w] else 0)

            if dx != 0 or dy != 0:
                mag = math.hypot(dx, dy)
                nx = dx / mag
                ny = dy / mag
                mv.set_velocity(nx * mv.speed, ny * mv.speed)
            else:
                mv.set_velocity(0, 0)
