"""Sammelt Pygame-Events und Eingaben in einer einheitlichen Struktur."""

import pygame as pg


def poll_input() -> dict:
    """Liest Events, Tastatur und Maus für einen Frame aus."""
    events = pg.event.get()
    keys = pg.key.get_pressed()
    mouse = {
        "pos": pg.mouse.get_pos(),
        "buttons": pg.mouse.get_pressed(3),
    }
    quit_requested = any(
        event.type == pg.QUIT
        or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE)
        for event in events
    )
    return {
        "quit": quit_requested,
        "keys": keys,
        "events": events,
        "mouse": mouse,
    }
