"""OpenGL-Initialisierung und einfache Zeichenfunktionen."""

import math
from collections.abc import Sequence

import pygame
from OpenGL.GL import (
    GL_BLEND,
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_MODELVIEW,
    GL_PROJECTION,
    GL_QUADS,
    GL_LINES,
    GL_LINE_LOOP,
    GL_TRIANGLE_FAN,
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
    glLineWidth,
    glViewport,
    glOrtho,
)
from OpenGL.GLU import gluPerspective


VERTEX_SHADER = """#version 120
void main() { gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex; }
"""
FRAGMENT_SHADER = """#version 120
void main() { gl_FragColor = gl_Color; }
"""

class Render_system:
    shader_program = None

    def init_opengl(width: int, height: int) -> None:
        """Richtet Kamera, Tiefentest und Hintergrundfarbe ein."""
        pygame.display.set_caption("Gambling")
        glViewport(0, 0, width, height)

        glClearColor(0.05, 0.05, 0.08, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        try:
            from OpenGL.GL.shaders import compileProgram, compileShader
            from OpenGL.GL import GL_VERTEX_SHADER, GL_FRAGMENT_SHADER
            Render_system.shader_program = compileProgram(
                compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
                compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER),
            )
        except Exception:
            Render_system.shader_program = None

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-12.0, 12.0, -12.0 * height / width, 12.0 * height / width, -30.0, 30.0)

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

        glBegin(GL_QUADS)
        glColor3f(0.12, 0.16, 0.14)
        glVertex3f(-half_size, 0.0, -half_size)
        glVertex3f(half_size, 0.0, -half_size)
        glVertex3f(half_size, 0.0, half_size)
        glVertex3f(-half_size, 0.0, half_size)
        glEnd()

        glColor3f(0.30, 0.30, 0.30)
        glLineWidth(1.0)
        glBegin(GL_LINES)
        for index in range(-5, 6):
            coordinate = index * 3.0
            glVertex3f(coordinate, 0.01, -half_size)
            glVertex3f(coordinate, 0.01, half_size)
            glVertex3f(-half_size, 0.01, coordinate)
            glVertex3f(half_size, 0.01, coordinate)
        glEnd()


    def draw_cylinder(
        pos: Sequence[float],
        radius: float,
        height: float,
        color: Sequence[float],
    ) -> None:
        """Draws a lit-looking low-poly body using immediate-mode geometry."""
        x, y, z = pos
        segments = 12
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(*color)
        glBegin(GL_QUADS)
        for index in range(segments):
            a1 = 6.283185 * index / segments
            a2 = 6.283185 * (index + 1) / segments
            glVertex3f(radius * math.cos(a1), 0.0, radius * math.sin(a1))
            glVertex3f(radius * math.cos(a2), 0.0, radius * math.sin(a2))
            glVertex3f(radius * math.cos(a2), height, radius * math.sin(a2))
            glVertex3f(radius * math.cos(a1), height, radius * math.sin(a1))
        glEnd()
        glColor3f(min(1.0, color[0] * 1.25), min(1.0, color[1] * 1.25), min(1.0, color[2] * 1.25))
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0.0, height, 0.0)
        for index in range(segments + 1):
            angle = 6.283185 * index / segments
            glVertex3f(radius * math.cos(angle), height, radius * math.sin(angle))
        glEnd()
        glPopMatrix()


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

    @staticmethod
    def draw_crosshair(x: float, y: float, size: float = 10.0) -> None:
        """Draw a screen-space crosshair in normalized pixel coordinates."""
        from OpenGL.GL import glColor3f, glBegin, glEnd, glVertex2f

        glColor3f(1.0, 0.85, 0.2)
        glBegin(GL_LINES)
        glVertex2f(x - size, y)
        glVertex2f(x + size, y)
        glVertex2f(x, y - size)
        glVertex2f(x, y + size)
        glEnd()

        glColor3f(0.22, 0.28, 0.23)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glVertex3f(-half_size, 0.03, -half_size)
        glVertex3f(half_size, 0.03, -half_size)
        glVertex3f(half_size, 0.03, -half_size)
        glVertex3f(half_size, 0.03, half_size)
        glVertex3f(half_size, 0.03, half_size)
        glVertex3f(-half_size, 0.03, half_size)
        glVertex3f(-half_size, 0.03, half_size)
        glVertex3f(-half_size, 0.03, -half_size)
        glEnd()