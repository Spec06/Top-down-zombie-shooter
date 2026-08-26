"""OpenGL-Initialisierung und einfache Zeichenfunktionen."""

from collections.abc import Sequence

import pygame
from OpenGL.GL import (
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_MODELVIEW,
    GL_PROJECTION,
    GL_QUADS,
    glBegin,
    glClear,
    glClearColor,
    glColor3f,
    glEnable,
    glEnd,
    glLoadIdentity,
    glMatrixMode,
    glPopMatrix,
    glPushMatrix,
    glTranslatef,
    glVertex3f,
)
from OpenGL.GLU import gluPerspective

class Render_system:
    def init_opengl(width: int, height: int) -> None:
        """Richtet Kamera, Tiefentest und Hintergrundfarbe ein."""
        pygame.display.set_caption("Gambling")

        glClearColor(0.08, 0.10, 0.14, 1.0)
        glEnable(GL_DEPTH_TEST)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60.0, width / height, 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()


    def begin_frame() -> None:
        """Löscht das Bild des vorherigen Frames."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()


    def end_frame() -> None:
        """Zeigt den fertig gezeichneten Frame an."""
        pygame.display.flip()


    def draw_ground(size: float = 30.0) -> None:
        """Zeichnet eine flache Bodenfläche auf Höhe y=0."""
        half_size = size / 2.0

        glColor3f(0.25, 0.30, 0.25)
        glBegin(GL_QUADS)
        glVertex3f(-half_size, 0.0, -half_size)
        glVertex3f(half_size, 0.0, -half_size)
        glVertex3f(half_size, 0.0, half_size)
        glVertex3f(-half_size, 0.0, half_size)
        glEnd()


    def draw_cube(
        pos: Sequence[float],
        size: float,
        color: Sequence[float],
    ) -> None:
        """Zeichnet einen farbigen Würfel an der Position pos."""
        x, y, z = pos
        half_size = size / 2.0
        red, green, blue = color

        vertices = (
            (-half_size, -half_size, -half_size),
            (half_size, -half_size, -half_size),
            (half_size, half_size, -half_size),
            (-half_size, half_size, -half_size),
            (-half_size, -half_size, half_size),
            (half_size, -half_size, half_size),
            (half_size, half_size, half_size),
            (-half_size, half_size, half_size),
        )

        faces = (
            (0, 1, 2, 3),
            (4, 5, 6, 7),
            (0, 1, 5, 4),
            (2, 3, 7, 6),
            (1, 2, 6, 5),
            (0, 3, 7, 4),
        )

        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(red, green, blue)

        glBegin(GL_QUADS)
        for face in faces:
            for vertex_index in face:
                glVertex3f(*vertices[vertex_index])
        glEnd()

        glPopMatrix()