#!/usr/bin/env python3
"""Simple test: open a pygame window with an OpenGL context and clear the screen.

Run with: `py tools/test_opengl.py` (activate your venv first).
Requirements: `pygame-ce` (or pygame) and `PyOpenGL` installed in the active environment.
"""
import sys

import pygame
from pygame.locals import DOUBLEBUF, OPENGL, QUIT, KEYDOWN, K_ESCAPE

try:
    from OpenGL.GL import glClearColor, glClear, glViewport, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT
except Exception as e:
    print("Failed to import OpenGL.GL: ", e)
    print("Make sure PyOpenGL (and optionally PyOpenGL-accelerate) is installed in the active environment.")
    sys.exit(1)


def main(width=800, height=600):
    pygame.init()

    # Request an OpenGL-capable display
    pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL test - press ESC or close window to quit")

    # Basic GL setup
    glViewport(0, 0, width, height)
    glClearColor(0.05, 0.1, 0.15, 1.0)

    running = True
    clock = pygame.time.Clock()

    while running:
        for ev in pygame.event.get():
            if ev.type == QUIT:
                running = False
            if ev.type == KEYDOWN and ev.key == K_ESCAPE:
                running = False

        # clear screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # swap buffers
        pygame.display.flip()

        # cap framerate
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print("Error while running OpenGL test:", exc)
        raise
