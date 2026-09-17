"""OpenGL-Initialisierung und einfache Zeichenfunktionen."""

import math
import ctypes
from collections.abc import Sequence

import pygame
import numpy as np
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
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader


def mat4_translate(x: float, y: float, z: float) -> np.ndarray:
    matrix = np.identity(4, dtype=np.float32)
    matrix[0, 3], matrix[1, 3], matrix[2, 3] = x, y, z
    return matrix


def mat4_scale(x: float, y: float, z: float) -> np.ndarray:
    matrix = np.identity(4, dtype=np.float32)
    matrix[0, 0], matrix[1, 1], matrix[2, 2] = x, y, z
    return matrix


def mat4_rotate_y(angle: float) -> np.ndarray:
    cosine, sine = math.cos(angle), math.sin(angle)
    matrix = np.identity(4, dtype=np.float32)
    matrix[0, 0], matrix[0, 2] = cosine, -sine
    matrix[2, 0], matrix[2, 2] = sine, cosine
    return matrix


def mat4_rotate_x(angle: float) -> np.ndarray:
    cosine, sine = math.cos(angle), math.sin(angle)
    matrix = np.identity(4, dtype=np.float32)
    matrix[1, 1], matrix[1, 2] = cosine, -sine
    matrix[2, 1], matrix[2, 2] = sine, cosine
    return matrix


def mat4_mul(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    return np.dot(first, second).astype(np.float32)


def mat4_identity() -> np.ndarray:
    return np.identity(4, dtype=np.float32)


def mat4_ortho(left: float, right: float, bottom: float, top: float, near: float, far: float) -> np.ndarray:
    matrix = np.identity(4, dtype=np.float32)
    matrix[0, 0] = 2.0 / (right - left)
    matrix[1, 1] = 2.0 / (top - bottom)
    matrix[2, 2] = -2.0 / (far - near)
    matrix[0, 3] = -(right + left) / (right - left)
    matrix[1, 3] = -(top + bottom) / (top - bottom)
    matrix[2, 3] = -(far + near) / (far - near)
    return matrix


def mat4_look_at(eye, target, up) -> np.ndarray:
    eye_vector = np.asarray(eye, dtype=np.float32)
    target_vector = np.asarray(target, dtype=np.float32)
    up_vector = np.asarray(up, dtype=np.float32)
    forward = target_vector - eye_vector
    forward /= np.linalg.norm(forward)
    side = np.cross(forward, up_vector)
    side /= np.linalg.norm(side)
    true_up = np.cross(side, forward)
    matrix = np.identity(4, dtype=np.float32)
    matrix[0, :3] = side
    matrix[0, 3] = -np.dot(side, eye_vector)
    matrix[1, :3] = true_up
    matrix[1, 3] = -np.dot(true_up, eye_vector)
    matrix[2, :3] = -forward
    matrix[2, 3] = np.dot(forward, eye_vector)
    return matrix


def make_cube():
    vertices, normals = [], []

    def face(first, second, third, fourth, normal):
        vertices.extend([first, second, third, first, third, fourth])
        normals.extend([normal] * 6)

    side = 0.5
    face([side, -side, -side], [side, side, -side], [side, side, side], [side, -side, side], [1, 0, 0])
    face([-side, -side, side], [-side, side, side], [-side, side, -side], [-side, -side, -side], [-1, 0, 0])
    face([-side, side, -side], [-side, side, side], [side, side, side], [side, side, -side], [0, 1, 0])
    face([-side, -side, side], [-side, -side, -side], [side, -side, -side], [side, -side, side], [0, -1, 0])
    face([-side, -side, side], [side, -side, side], [side, side, side], [-side, side, side], [0, 0, 1])
    face([side, -side, -side], [-side, -side, -side], [-side, side, -side], [side, side, -side], [0, 0, -1])
    return np.array(vertices, dtype=np.float32), np.array(normals, dtype=np.float32)


def make_cylinder(radius=0.5, height=1.0, segments=16):
    vertices, normals = [], []
    for index in range(segments):
        first_angle = 2 * math.pi * index / segments
        second_angle = 2 * math.pi * (index + 1) / segments
        x1, z1 = math.cos(first_angle) * radius, math.sin(first_angle) * radius
        x2, z2 = math.cos(second_angle) * radius, math.sin(second_angle) * radius
        normal1 = (math.cos(first_angle), 0, math.sin(first_angle))
        normal2 = (math.cos(second_angle), 0, math.sin(second_angle))
        vertices.extend([[x1, 0, z1], [x2, 0, z2], [x1, height, z1], [x2, 0, z2], [x2, height, z2], [x1, height, z1]])
        normals.extend([normal1, normal2, normal1, normal2, normal2, normal1])
    for index in range(segments):
        first_angle = 2 * math.pi * index / segments
        second_angle = 2 * math.pi * (index + 1) / segments
        x1, z1 = math.cos(first_angle) * radius, math.sin(first_angle) * radius
        x2, z2 = math.cos(second_angle) * radius, math.sin(second_angle) * radius
        vertices.extend([[0, height, 0], [x1, height, z1], [x2, height, z2], [0, 0, 0], [x2, 0, z2], [x1, 0, z1]])
        normals.extend([[0, 1, 0]] * 3 + [[0, -1, 0]] * 3)
    return np.array(vertices, dtype=np.float32), np.array(normals, dtype=np.float32)


def make_quad():
    vertices = [[-0.5, 0, -0.5], [0.5, 0, -0.5], [0.5, 0, 0.5], [-0.5, 0, -0.5], [0.5, 0, 0.5], [-0.5, 0, 0.5]]
    return np.array(vertices, dtype=np.float32), np.array([[0, 1, 0]] * 6, dtype=np.float32)


def make_hud_quad():
    vertices = [[-0.5, -0.5, 0], [0.5, -0.5, 0], [0.5, 0.5, 0], [-0.5, -0.5, 0], [0.5, 0.5, 0], [-0.5, 0.5, 0]]
    texcoords = [[0, 1], [1, 1], [1, 0], [0, 1], [1, 0], [0, 0]]
    return np.array(vertices, dtype=np.float32), np.array(texcoords, dtype=np.float32)


class TextRenderer:
    """Cache pygame font textures used by the OpenGL renderer."""

    def __init__(self):
        self.cache = {}
        pygame.font.init()
        self.fonts = {
            "tiny": pygame.font.SysFont("Arial", 14, bold=True),
            "small": pygame.font.SysFont("Arial", 18, bold=True),
            "med": pygame.font.SysFont("Arial", 24, bold=True),
            "large": pygame.font.SysFont("Arial", 40, bold=True),
            "huge": pygame.font.SysFont("Arial", 72, bold=True),
        }

    def get_texture(self, text, font_key, color):
        key = (text, font_key, color)
        if key in self.cache:
            return self.cache[key]
        surface = self.fonts[font_key].render(str(text), True, color)
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, surface.get_width(), surface.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, pygame.image.tostring(surface, "RGBA", True))
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glBindTexture(GL_TEXTURE_2D, 0)
        self.cache[key] = (texture, surface.get_width(), surface.get_height())
        return self.cache[key]


PHONG_VS = """#version 330 core
layout(location=0) in vec3 aPos;
layout(location=1) in vec3 aNormal;
uniform mat4 uModel, uView, uProj;
out vec3 vNormal, vWorldPos;
void main() {
    vec4 wp = uModel * vec4(aPos, 1.0);
    vWorldPos = wp.xyz;
    vNormal = mat3(uModel) * aNormal;
    gl_Position = uProj * uView * wp;
}
"""
PHONG_FS = """#version 330 core
in vec3 vNormal, vWorldPos;
uniform vec3 uColor, uLightDir, uViewPos, uPlayerPos, uEmissive;
uniform float uSpotlight, uAlpha;
out vec4 FragColor;
void main() {
    vec3 N = normalize(vNormal);
    vec3 L = normalize(-uLightDir);
    float ambient = 0.45;
    float diff = max(dot(N, L), 0.0);
    vec3 V = normalize(uViewPos - vWorldPos);
    vec3 R = reflect(-L, N);
    float spec = pow(max(dot(V, R), 0.0), 32.0) * 0.4;
    vec3 color = uColor * (ambient + diff * 0.7) + vec3(spec) + uEmissive;
    if (uSpotlight > 0.5) {
        float d = length(vWorldPos.xz - uPlayerPos.xz);
        color *= (0.35 + 0.65 * (1.0 - smoothstep(12.0, 25.0, d)));
    }
    FragColor = vec4(color, uAlpha);
}
"""
FLAT_VS = """#version 330 core
layout(location=0) in vec3 aPos;
uniform mat4 uModel, uProj;
void main() { gl_Position = uProj * uModel * vec4(aPos, 1.0); }
"""
FLAT_FS = """#version 330 core
uniform vec4 uColor;
out vec4 FragColor;
void main() { FragColor = uColor; }
"""
TEXT_VS = """#version 330 core
layout(location=0) in vec3 aPos;
layout(location=1) in vec2 aTexCoord;
uniform mat4 uModel, uProj;
out vec2 vTexCoord;
void main() { gl_Position = uProj * uModel * vec4(aPos, 1.0); vTexCoord = aTexCoord; }
"""
TEXT_FS = """#version 330 core
in vec2 vTexCoord;
uniform sampler2D uTex;
uniform vec4 uColor;
out vec4 FragColor;
void main() { FragColor = vec4(uColor.rgb, texture(uTex, vTexCoord).a * uColor.a); }
"""


class GameRenderer:
    """Shader-based renderer used by the game loop."""

    def __init__(self, width: int, height: int):
        self.w, self.h = width, height
        glViewport(0, 0, width, height)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_CULL_FACE)
        self.prog_phong = self._make_program(PHONG_VS, PHONG_FS)
        self.prog_flat = self._make_program(FLAT_VS, FLAT_FS)
        self.prog_text = self._make_program(TEXT_VS, TEXT_FS)
        self.p_uModel = glGetUniformLocation(self.prog_phong, "uModel")
        self.p_uView = glGetUniformLocation(self.prog_phong, "uView")
        self.p_uProj = glGetUniformLocation(self.prog_phong, "uProj")
        self.p_uColor = glGetUniformLocation(self.prog_phong, "uColor")
        self.p_uLightDir = glGetUniformLocation(self.prog_phong, "uLightDir")
        self.p_uViewPos = glGetUniformLocation(self.prog_phong, "uViewPos")
        self.p_uPlayerPos = glGetUniformLocation(self.prog_phong, "uPlayerPos")
        self.p_uEmissive = glGetUniformLocation(self.prog_phong, "uEmissive")
        self.p_uSpotlight = glGetUniformLocation(self.prog_phong, "uSpotlight")
        self.p_uAlpha = glGetUniformLocation(self.prog_phong, "uAlpha")
        self.f_uModel = glGetUniformLocation(self.prog_flat, "uModel")
        self.f_uProj = glGetUniformLocation(self.prog_flat, "uProj")
        self.f_uColor = glGetUniformLocation(self.prog_flat, "uColor")
        self.t_uModel = glGetUniformLocation(self.prog_text, "uModel")
        self.t_uProj = glGetUniformLocation(self.prog_text, "uProj")
        self.t_uTex = glGetUniformLocation(self.prog_text, "uTex")
        self.t_uColor = glGetUniformLocation(self.prog_text, "uColor")
        cube_vertices, cube_normals = make_cube()
        self.cube_vao, self.cube_count = self._make_vao_pos_norm(cube_vertices, cube_normals)
        cylinder_vertices, cylinder_normals = make_cylinder()
        self.cyl_vao, self.cyl_count = self._make_vao_pos_norm(cylinder_vertices, cylinder_normals)
        quad_vertices, quad_normals = make_quad()
        self.quad_vao, self.quad_count = self._make_vao_pos_norm(quad_vertices, quad_normals)
        hud_vertices, hud_texcoords = make_hud_quad()
        self.hud_vao, self.hud_count = self._make_vao_pos_tex(hud_vertices, hud_texcoords)
        self.cur_view = mat4_identity()
        self.cur_proj = mat4_identity()
        self.cur_view_pos = np.array([0, 30, 20], dtype=np.float32)
        self.cur_player_pos = np.array([0, 0, 0], dtype=np.float32)
        self.light_dir = np.array([0.5, -1.0, -0.3], dtype=np.float32)
        self.spotlight_on = 1.0

    @staticmethod
    def _make_program(vertex_source, fragment_source):
        return compileProgram(compileShader(vertex_source, GL_VERTEX_SHADER), compileShader(fragment_source, GL_FRAGMENT_SHADER))

    def _make_vao_pos_norm(self, vertices, normals):
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)
        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        data = np.hstack([vertices, normals]).astype(np.float32)
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, None)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glBindVertexArray(0)
        return vao, len(vertices)

    def _make_vao_pos_tex(self, vertices, texcoords):
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)
        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        data = np.hstack([vertices, texcoords]).astype(np.float32)
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, None)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))
        glBindVertexArray(0)
        return vao, len(vertices)

    def begin_3d(self, view, projection, view_position, player_position, spotlight=True):
        self.cur_view, self.cur_proj = view, projection
        self.cur_view_pos = np.asarray(view_position, dtype=np.float32)
        self.cur_player_pos = np.asarray(player_position, dtype=np.float32)
        self.spotlight_on = 1.0 if spotlight else 0.0
        glUseProgram(self.prog_phong)
        glUniformMatrix4fv(self.p_uView, 1, GL_TRUE, view)
        glUniformMatrix4fv(self.p_uProj, 1, GL_TRUE, projection)
        glUniform3f(self.p_uLightDir, *self.light_dir)
        glUniform3f(self.p_uViewPos, *self.cur_view_pos)
        glUniform3f(self.p_uPlayerPos, *self.cur_player_pos)
        glUniform1f(self.p_uSpotlight, self.spotlight_on)
        glEnable(GL_DEPTH_TEST)

    def _draw_phong(self, model, color, emissive, alpha, vao, count):
        glUseProgram(self.prog_phong)
        glUniformMatrix4fv(self.p_uView, 1, GL_TRUE, self.cur_view)
        glUniformMatrix4fv(self.p_uProj, 1, GL_TRUE, self.cur_proj)
        glUniformMatrix4fv(self.p_uModel, 1, GL_TRUE, model)
        glUniform3f(self.p_uColor, *color)
        glUniform3f(self.p_uEmissive, *emissive)
        glUniform1f(self.p_uAlpha, alpha)
        glUniform3f(self.p_uViewPos, *self.cur_view_pos)
        glUniform3f(self.p_uPlayerPos, *self.cur_player_pos)
        glUniform1f(self.p_uSpotlight, self.spotlight_on)
        glBindVertexArray(vao)
        glDrawArrays(GL_TRIANGLES, 0, count)

    def draw_cube(self, model, color, emissive=(0, 0, 0), alpha=1.0):
        self._draw_phong(model, color, emissive, alpha, self.cube_vao, self.cube_count)

    def draw_cylinder(self, model, color, emissive=(0, 0, 0), alpha=1.0):
        self._draw_phong(model, color, emissive, alpha, self.cyl_vao, self.cyl_count)

    def draw_quad(self, model, color, emissive=(0, 0, 0), alpha=1.0):
        self._draw_phong(model, color, emissive, alpha, self.quad_vao, self.quad_count)

    def begin_hud(self):
        glDisable(GL_DEPTH_TEST)
        self.hud_proj = mat4_ortho(0, self.w, self.h, 0, -1, 1)

    def draw_hud_quad(self, x, y, width, height, color, alpha=1.0):
        glUseProgram(self.prog_flat)
        model = mat4_mul(mat4_translate(x + width / 2, y + height / 2, 0), mat4_scale(width, height, 1))
        glUniformMatrix4fv(self.f_uModel, 1, GL_TRUE, model)
        glUniformMatrix4fv(self.f_uProj, 1, GL_TRUE, self.hud_proj)
        glUniform4f(self.f_uColor, color[0], color[1], color[2], alpha)
        glBindVertexArray(self.hud_vao)
        glDrawArrays(GL_TRIANGLES, 0, self.hud_count)

    def draw_text(self, text_renderer, text, x, y, font_key, color, alpha=1.0, center=False, scale=1.0):
        texture, width, height = text_renderer.get_texture(text, font_key, color)
        if center:
            x -= width // 2
        glUseProgram(self.prog_text)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture)
        glUniform1i(self.t_uTex, 0)
        model = mat4_mul(mat4_translate(x + width * scale / 2, y + height * scale / 2, 0), mat4_scale(width * scale, height * scale, 1))
        glUniformMatrix4fv(self.t_uModel, 1, GL_TRUE, model)
        glUniformMatrix4fv(self.t_uProj, 1, GL_TRUE, self.hud_proj)
        glUniform4f(self.t_uColor, 1.0, 1.0, 1.0, alpha)
        glBindVertexArray(self.hud_vao)
        glDrawArrays(GL_TRIANGLES, 0, self.hud_count)

    def end_hud(self):
        glEnable(GL_DEPTH_TEST)


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