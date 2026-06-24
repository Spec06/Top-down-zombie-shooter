# pip install pygame PyOpenGL numpy
# Run: python main_game.py

"""
3D Top-Down Zombie Looter Shooter - Single File Implementation
All assets are procedurally generated. No external files needed.
"""

import sys, math, random, ctypes
import numpy as np
import pygame
from pygame import mixer
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram

# ============================================================
# Constants
# ============================================================
SCREEN_W, SCREEN_H = 1920, 1080
FPS = 120
WORLD_HALF = 50.0

STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER = 0, 1, 2, 3

WEAPONS = {
    'pistol':  dict(name='Pistol',  damage=15, fire_rate=0.25, magazine=12, reload_time=1.2, spread=0.02,  bullet_speed=40, pellets=1, color=(0.9,0.9,0.3), auto=False),
    'shotgun': dict(name='Shotgun', damage=8,  fire_rate=0.8,  magazine=6,  reload_time=2.0, spread=0.15,  bullet_speed=35, pellets=6, color=(0.9,0.6,0.2), auto=False),
    'rifle':   dict(name='Rifle',   damage=35, fire_rate=0.12, magazine=20, reload_time=1.8, spread=0.005, bullet_speed=60, pellets=1, color=(0.3,0.7,0.9), auto=True),
}
WEAPON_ORDER = ['pistol', 'shotgun', 'rifle']

ZOMBIE_TYPES = {
    'normal': dict(hp=50,  speed=2.5, damage=10, color=(0.4,0.5,0.2), size=(0.6,1.6,0.6)),
    'fast':   dict(hp=25,  speed=5.0, damage=7,  color=(0.6,0.4,0.2), size=(0.4,1.4,0.4)),
    'tank':   dict(hp=100, speed=1.3, damage=20, color=(0.3,0.3,0.2), size=(1.0,2.2,1.0)),
}

# ============================================================
# Matrix Math
# ============================================================
def mat4_identity():
    return np.identity(4, dtype=np.float32)

def mat4_translate(x, y, z):
    m = np.identity(4, dtype=np.float32)
    m[0,3], m[1,3], m[2,3] = x, y, z
    return m

def mat4_scale(sx, sy, sz):
    m = np.identity(4, dtype=np.float32)
    m[0,0], m[1,1], m[2,2] = sx, sy, sz
    return m

def mat4_rotate_y(a):
    c, s = math.cos(a), math.sin(a)
    m = np.identity(4, dtype=np.float32)
    m[0,0], m[0,2] = c, -s
    m[2,0], m[2,2] = s, c
    return m

def mat4_rotate_x(a):
    c, s = math.cos(a), math.sin(a)
    m = np.identity(4, dtype=np.float32)
    m[1,1], m[1,2] = c, -s
    m[2,1], m[2,2] = s, c
    return m

def mat4_ortho(l, r, b, t, n, f):
    m = np.identity(4, dtype=np.float32)
    m[0,0] = 2.0/(r-l); m[1,1] = 2.0/(t-b); m[2,2] = -2.0/(f-n)
    m[0,3] = -(r+l)/(r-l); m[1,3] = -(t+b)/(t-b); m[2,3] = -(f+n)/(f-n)
    return m

def mat4_look_at(eye, target, up):
    eye = np.array(eye, dtype=np.float32)
    target = np.array(target, dtype=np.float32)
    up = np.array(up, dtype=np.float32)
    f = target - eye; f /= np.linalg.norm(f)
    s = np.cross(f, up); s /= np.linalg.norm(s)
    u = np.cross(s, f)
    m = np.identity(4, dtype=np.float32)
    m[0,0]=s[0]; m[0,1]=s[1]; m[0,2]=s[2]; m[0,3]=-np.dot(s,eye)
    m[1,0]=u[0]; m[1,1]=u[1]; m[1,2]=u[2]; m[1,3]=-np.dot(u,eye)
    m[2,0]=-f[0]; m[2,1]=-f[1]; m[2,2]=-f[2]; m[2,3]=np.dot(f,eye)
    return m

def mat4_mul(a, b):
    return np.dot(a, b).astype(np.float32)

# ============================================================
# Shaders
# ============================================================
PHONG_VS = """
#version 330 core
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
PHONG_FS = """
#version 330 core
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
    vec3 color = uColor * (ambient + diff * 0.7) + vec3(spec);
    color += uEmissive;
    if (uSpotlight > 0.5) {
        float d = length(vWorldPos.xz - uPlayerPos.xz);
        float s = 1.0 - smoothstep(12.0, 25.0, d);
        color *= (0.35 + 0.65 * s);
    }
    FragColor = vec4(color, uAlpha);
}
"""
FLAT_VS = """
#version 330 core
layout(location=0) in vec3 aPos;
uniform mat4 uModel, uProj;
void main() { gl_Position = uProj * uModel * vec4(aPos, 1.0); }
"""
FLAT_FS = """
#version 330 core
uniform vec4 uColor;
out vec4 FragColor;
void main() { FragColor = uColor; }
"""
TEXT_VS = """
#version 330 core
layout(location=0) in vec3 aPos;
layout(location=1) in vec2 aTexCoord;
uniform mat4 uModel, uProj;
out vec2 vTexCoord;
void main() { gl_Position = uProj * uModel * vec4(aPos, 1.0); vTexCoord = aTexCoord; }
"""
TEXT_FS = """
#version 330 core
in vec2 vTexCoord;
uniform sampler2D uTex;
uniform vec4 uColor;
out vec4 FragColor;
void main() {
    float a = texture(uTex, vTexCoord).a;
    FragColor = vec4(uColor.rgb, a * uColor.a);
}
"""

# ============================================================
# Geometry Generation
# ============================================================
def make_cube():
    verts, norms = [], []
    def face(p1, p2, p3, p4, n):
        verts.extend([p1, p2, p3, p1, p3, p4])
        norms.extend([n]*6)
    s = 0.5
    face([ s,-s,-s],[ s, s,-s],[ s, s, s],[ s,-s, s],[1,0,0])
    face([-s,-s, s],[-s, s, s],[-s, s,-s],[-s,-s,-s],[-1,0,0])
    face([-s, s,-s],[-s, s, s],[ s, s, s],[ s, s,-s],[0,1,0])
    face([-s,-s, s],[-s,-s,-s],[ s,-s,-s],[ s,-s, s],[0,-1,0])
    face([-s,-s, s],[ s,-s, s],[ s, s, s],[-s, s, s],[0,0,1])
    face([ s,-s,-s],[-s,-s,-s],[-s, s,-s],[ s, s,-s],[0,0,-1])
    return np.array(verts, dtype=np.float32), np.array(norms, dtype=np.float32)

def make_cylinder(radius=0.5, height=1.0, segments=16):
    verts, norms = [], []
    r, h = radius, height
    for i in range(segments):
        a1 = 2*math.pi*i/segments; a2 = 2*math.pi*(i+1)/segments
        x1, z1 = math.cos(a1)*r, math.sin(a1)*r
        x2, z2 = math.cos(a2)*r, math.sin(a2)*r
        n1 = (math.cos(a1), 0, math.sin(a1))
        n2 = (math.cos(a2), 0, math.sin(a2))
        verts.extend([[x1,0,z1],[x2,0,z2],[x1,h,z1]])
        norms.extend([n1,n2,n1])
        verts.extend([[x2,0,z2],[x2,h,z2],[x1,h,z1]])
        norms.extend([n2,n2,n1])
    for i in range(segments):
        a1 = 2*math.pi*i/segments; a2 = 2*math.pi*(i+1)/segments
        x1, z1 = math.cos(a1)*r, math.sin(a1)*r
        x2, z2 = math.cos(a2)*r, math.sin(a2)*r
        verts.extend([[0,h,0],[x1,h,z1],[x2,h,z2]])
        norms.extend([[0,1,0]]*3)
        verts.extend([[0,0,0],[x2,0,z2],[x1,0,z1]])
        norms.extend([[0,-1,0]]*3)
    return np.array(verts, dtype=np.float32), np.array(norms, dtype=np.float32)

def make_quad():
    # XZ plane quad, y=0, size 1x1
    verts = [
        [-0.5,0,-0.5],[0.5,0,-0.5],[0.5,0,0.5],
        [-0.5,0,-0.5],[0.5,0,0.5],[-0.5,0,0.5],
    ]
    norms = [[0,1,0]]*6
    return np.array(verts, dtype=np.float32), np.array(norms, dtype=np.float32)

def make_hud_quad():
    # XY plane quad, centered at origin, size 1x1
    verts = [
        [-0.5,-0.5,0],[0.5,-0.5,0],[0.5,0.5,0],
        [-0.5,-0.5,0],[0.5,0.5,0],[-0.5,0.5,0],
    ]
    texcoords = [
        [0,0],[1,0],[1,1],
        [0,0],[1,1],[0,1],
    ]
    return np.array(verts, dtype=np.float32), np.array(texcoords, dtype=np.float32)

# ============================================================
# Text Renderer
# ============================================================
class TextRenderer:
    def __init__(self):
        self.cache = {}
        pygame.font.init()
        self.fonts = {
            'tiny':  pygame.font.SysFont('Arial', 14, bold=True),
            'small': pygame.font.SysFont('Arial', 18, bold=True),
            'med':   pygame.font.SysFont('Arial', 24, bold=True),
            'large': pygame.font.SysFont('Arial', 40, bold=True),
            'huge':  pygame.font.SysFont('Arial', 72, bold=True),
        }

    def get_texture(self, text, font_key, color):
        key = (text, font_key, color)
        if key in self.cache:
            return self.cache[key]
        font = self.fonts[font_key]
        surf = font.render(str(text), True, color)
        data = pygame.image.tostring(surf, 'RGBA', True)
        w, h = surf.get_size()
        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glBindTexture(GL_TEXTURE_2D, 0)
        self.cache[key] = (tex, w, h)
        return self.cache[key]

# ============================================================
# Renderer
# ============================================================
class Renderer:
    def __init__(self, w, h):
        self.w, self.h = w, h
        glViewport(0, 0, w, h)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_CULL_FACE)
        
        self.prog_phong = self._make_program(PHONG_VS, PHONG_FS)
        self.prog_flat = self._make_program(FLAT_VS, FLAT_FS)
        self.prog_text = self._make_program(TEXT_VS, TEXT_FS)
        
        # Phong uniform locations
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
        
        # Flat uniform locations
        self.f_uModel = glGetUniformLocation(self.prog_flat, "uModel")
        self.f_uProj = glGetUniformLocation(self.prog_flat, "uProj")
        self.f_uColor = glGetUniformLocation(self.prog_flat, "uColor")
        
        # Text uniform locations
        self.t_uModel = glGetUniformLocation(self.prog_text, "uModel")
        self.t_uProj = glGetUniformLocation(self.prog_text, "uProj")
        self.t_uTex = glGetUniformLocation(self.prog_text, "uTex")
        self.t_uColor = glGetUniformLocation(self.prog_text, "uColor")
        
        cv, cn = make_cube()
        self.cube_vao, self.cube_count = self._make_vao_pos_norm(cv, cn)
        cyv, cyn = make_cylinder()
        self.cyl_vao, self.cyl_count = self._make_vao_pos_norm(cyv, cyn)
        qv, qn = make_quad()
        self.quad_vao, self.quad_count = self._make_vao_pos_norm(qv, qn)
        hv, ht = make_hud_quad()
        self.hud_vao, self.hud_count = self._make_vao_pos_tex(hv, ht)
        
        # State
        self.cur_view = mat4_identity()
        self.cur_proj = mat4_identity()
        self.cur_view_pos = np.array([0,30,20], dtype=np.float32)
        self.cur_player_pos = np.array([0,0,0], dtype=np.float32)
        self.light_dir = np.array([0.5, -1.0, -0.3], dtype=np.float32)
        self.spotlight_on = 1.0

    def _make_program(self, vs_src, fs_src):
        vs = compileShader(vs_src, GL_VERTEX_SHADER)
        fs = compileShader(fs_src, GL_FRAGMENT_SHADER)
        return compileProgram(vs, fs)

    def _make_vao_pos_norm(self, verts, norms):
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)
        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        data = np.hstack([verts, norms]).astype(np.float32)
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
        stride = 24
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, None)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        glBindVertexArray(0)
        return vao, len(verts)

    def _make_vao_pos_tex(self, verts, texcoords):
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)
        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        data = np.hstack([verts, texcoords]).astype(np.float32)
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
        stride = 20
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, None)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        glBindVertexArray(0)
        return vao, len(verts)

    def begin_3d(self, view, proj, view_pos, player_pos, spotlight=True):
        self.cur_view = view
        self.cur_proj = proj
        self.cur_view_pos = np.array(view_pos, dtype=np.float32)
        self.cur_player_pos = np.array(player_pos, dtype=np.float32)
        self.spotlight_on = 1.0 if spotlight else 0.0
        glUseProgram(self.prog_phong)
        glUniformMatrix4fv(self.p_uView, 1, GL_TRUE, view)
        glUniformMatrix4fv(self.p_uProj, 1, GL_TRUE, proj)
        glUniform3f(self.p_uLightDir, *self.light_dir)
        glUniform3f(self.p_uViewPos, *self.cur_view_pos)
        glUniform3f(self.p_uPlayerPos, *self.cur_player_pos)
        glUniform1f(self.p_uSpotlight, self.spotlight_on)
        glEnable(GL_DEPTH_TEST)

    def draw_cube(self, model, color, emissive=(0,0,0), alpha=1.0):
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
        glBindVertexArray(self.cube_vao)
        glDrawArrays(GL_TRIANGLES, 0, self.cube_count)

    def draw_cylinder(self, model, color, emissive=(0,0,0), alpha=1.0):
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
        glBindVertexArray(self.cyl_vao)
        glDrawArrays(GL_TRIANGLES, 0, self.cyl_count)

    def draw_quad(self, model, color, emissive=(0,0,0), alpha=1.0):
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
        glBindVertexArray(self.quad_vao)
        glDrawArrays(GL_TRIANGLES, 0, self.quad_count)

    def begin_hud(self):
        glDisable(GL_DEPTH_TEST)
        self.hud_proj = mat4_ortho(0, self.w, self.h, 0, -1, 1)

    def draw_hud_quad(self, x, y, w, h, color, alpha=1.0):
        glUseProgram(self.prog_flat)
        model = mat4_mul(mat4_translate(x + w/2, y + h/2, 0), mat4_scale(w, h, 1))
        glUniformMatrix4fv(self.f_uModel, 1, GL_TRUE, model)
        glUniformMatrix4fv(self.f_uProj, 1, GL_TRUE, self.hud_proj)
        glUniform4f(self.f_uColor, color[0], color[1], color[2], alpha)
        glBindVertexArray(self.hud_vao)
        glDrawArrays(GL_TRIANGLES, 0, self.hud_count)

    def draw_hud_text(self, text, x, y, font_key, color, alpha=1.0, center=False):
        tex, w, h = self.text_cache.get_texture(text, font_key, color) if hasattr(self, 'text_cache') else (None, 0, 0)
        # Use the text renderer passed externally
        pass

    def draw_text(self, text_renderer, text, x, y, font_key, color, alpha=1.0, center=False, scale=1.0):
        tex, w, h = text_renderer.get_texture(text, font_key, color)
        if center:
            x -= w // 2
        glUseProgram(self.prog_text)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, tex)
        glUniform1i(self.t_uTex, 0)
        model = mat4_mul(mat4_translate(x + (w*scale)/2, y + (h*scale)/2, 0),
        mat4_scale(w*scale, h*scale, 1))
        glUniformMatrix4fv(self.t_uModel, 1, GL_TRUE, model)
        glUniformMatrix4fv(self.t_uProj, 1, GL_TRUE, self.hud_proj)
        glUniform4f(self.t_uColor, 1.0, 1.0, 1.0, alpha)
        glBindVertexArray(self.hud_vao)
        glDrawArrays(GL_TRIANGLES, 0, self.hud_count)

    def end_hud(self):
        glEnable(GL_DEPTH_TEST)

# ============================================================
# Collision Helpers
# ============================================================
def check_obstacle_collision(x, z, half_size, obstacles, walls):
    for obs in obstacles:
        if abs(x - obs['x']) < (half_size + obs['w']/2) and abs(z - obs['z']) < (half_size + obs['d']/2):
            return True
    for w in walls:
        if abs(x - w['x']) < (half_size + w['w']/2) and abs(z - w['z']) < (half_size + w['d']/2):
            return True
    return False

# ============================================================
# Player
# ============================================================
class Player:
    WALK_SPEED = 5.0
    SPRINT_SPEED = 9.0
    MAX_HP = 100
    MAX_STAMINA = 100

    def __init__(self):
        self.pos = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.aim_angle = 0.0
        self.hp = self.MAX_HP
        self.stamina = self.MAX_STAMINA
        self.weapons = ['pistol', None, None]  # 3 slots
        self.current_weapon = 0
        self.ammo = {'pistol': 48, 'shotgun': 0, 'rifle': 0}
        self.magazine = {'pistol': 12, 'shotgun': 6, 'rifle': 20}
        self.consumables = 1  # medkits
        self.fire_cooldown = 0
        self.reloading = False
        self.reload_timer = 0
        self.hit_flash = 0
        self.muzzle_flash = 0
        self.hurt_cooldown = 0

    @property
    def current_weapon_key(self):
        return self.weapons[self.current_weapon]

    def switch_weapon(self, idx):
        if 0 <= idx < 3 and self.weapons[idx] is not None:
            self.current_weapon = idx
            self.reloading = False
            self.fire_cooldown = 0

    def try_shoot(self, game):
        if self.reloading or self.fire_cooldown > 0:
            return
        wkey = self.current_weapon_key
        if wkey is None:
            return
        w = WEAPONS[wkey]
        if self.magazine[wkey] <= 0:
            game.play_sound('empty')
            self.reload(game)
            return
        self.magazine[wkey] -= 1
        self.fire_cooldown = w['fire_rate']
        self.muzzle_flash = 0.05
        # Spawn bullets
        for i in range(w['pellets']):
            spread = random.uniform(-w['spread'], w['spread']) * (i + 1) if w['pellets'] > 1 else random.uniform(-w['spread'], w['spread'])
            angle = self.aim_angle + spread
            dir_vec = np.array([math.cos(angle), 0, math.sin(angle)], dtype=np.float32)
            spawn_pos = self.pos + dir_vec * 0.8
            spawn_pos[1] = 0.9
            vel = dir_vec * w['bullet_speed']
            b = Bullet(spawn_pos, vel, w['damage'], w['color'], 'player')
            game.bullets.append(b)
        game.play_sound('shoot_' + wkey)

    def reload(self, game):
        if self.reloading:
            return
        wkey = self.current_weapon_key
        if wkey is None:
            return
        w = WEAPONS[wkey]
        if self.magazine[wkey] >= w['magazine']:
            return
        if self.ammo[wkey] <= 0:
            return
        self.reloading = True
        self.reload_timer = 0
        game.play_sound('reload')

    def _complete_reload(self):
        wkey = self.current_weapon_key
        w = WEAPONS[wkey]
        needed = w['magazine'] - self.magazine[wkey]
        taken = min(needed, self.ammo[wkey])
        self.magazine[wkey] += taken
        self.ammo[wkey] -= taken
        self.reloading = False

    def take_damage(self, amount, game):
        if self.hurt_cooldown > 0:
            return
        self.hp = max(0, self.hp - amount)
        self.hit_flash = 0.2
        self.hurt_cooldown = 0.5
        game.shake(0.3, 0.4)
        game.play_sound('hurt')

    def use_medkit(self, game):
        if self.consumables > 0 and self.hp < self.MAX_HP:
            self.consumables -= 1
            self.hp = min(self.MAX_HP, self.hp + 50)
            game.add_feedback("+50 HP", self.pos[:], (0, 1, 0))
            game.play_sound('pickup')

    def pickup_loot(self, loot, game):
        if loot.type == 'ammo_pistol':
            self.ammo['pistol'] += 20
            game.add_feedback("Pistol Ammo +20", self.pos[:], (1, 1, 0))
        elif loot.type == 'ammo_shotgun':
            self.ammo['shotgun'] += 6
            game.add_feedback("Shotgun Ammo +6", self.pos[:], (1, 1, 0))
        elif loot.type == 'ammo_rifle':
            self.ammo['rifle'] += 20
            game.add_feedback("Rifle Ammo +20", self.pos[:], (1, 1, 0))
        elif loot.type == 'medkit':
            if self.consumables < 5:
                self.consumables += 1
                game.add_feedback("Medkit +1", self.pos[:], (1, 0, 0))
            else:
                return False
        elif loot.type == 'weapon_shotgun':
            if self.weapons[1] is None:
                self.weapons[1] = 'shotgun'
                game.add_feedback("Shotgun Acquired", self.pos[:], (0, 0.5, 1))
            else:
                self.ammo['shotgun'] += 6
                game.add_feedback("Shotgun Ammo +6", self.pos[:], (1, 1, 0))
        elif loot.type == 'weapon_rifle':
            if self.weapons[2] is None:
                self.weapons[2] = 'rifle'
                game.add_feedback("Rifle Acquired", self.pos[:], (0, 0.5, 1))
            else:
                self.ammo['rifle'] += 20
                game.add_feedback("Rifle Ammo +20", self.pos[:], (1, 1, 0))
        game.play_sound('pickup')
        return True

    def update(self, dt, game, keys):
        # Movement
        dx = (1 if keys[pygame.K_d] else 0) - (1 if keys[pygame.K_a] else 0)
        dz = (1 if keys[pygame.K_s] else 0) - (1 if keys[pygame.K_w] else 0)
        mag = math.hypot(dx, dz)
        if mag > 0:
            dx /= mag; dz /= mag

        sprinting = keys[pygame.K_LSHIFT] and self.stamina > 5 and mag > 0
        speed = self.SPRINT_SPEED if sprinting else self.WALK_SPEED
        if sprinting:
            self.stamina = max(0, self.stamina - 35 * dt)
        else:
            self.stamina = min(self.MAX_STAMINA, self.stamina + 18 * dt)

        new_x = self.pos[0] + dx * speed * dt
        new_z = self.pos[2] + dz * speed * dt
        if not check_obstacle_collision(new_x, self.pos[2], 0.4, game.obstacles, game.walls):
            self.pos[0] = max(-WORLD_HALF+1, min(WORLD_HALF-1, new_x))
        if not check_obstacle_collision(self.pos[0], new_z, 0.4, game.obstacles, game.walls):
            self.pos[2] = max(-WORLD_HALF+1, min(WORLD_HALF-1, new_z))

        # Aim
        self.aim_angle = math.atan2(game.mouse_world[2] - self.pos[2],
        game.mouse_world[0] - self.pos[0])

        # Auto-fire for auto weapons
        mouse = pygame.mouse.get_pressed()
        if mouse[0] and self.current_weapon_key:
            w = WEAPONS[self.current_weapon_key]
            if w['auto']:
                self.try_shoot(game)

        # Reload progress
        if self.reloading:
            self.reload_timer += dt
            w = WEAPONS[self.current_weapon_key]
            if self.reload_timer >= w['reload_time']:
                self._complete_reload()

        # Cooldowns
        if self.fire_cooldown > 0:
            self.fire_cooldown -= dt
        if self.hit_flash > 0:
            self.hit_flash -= dt
        if self.muzzle_flash > 0:
            self.muzzle_flash -= dt
        if self.hurt_cooldown > 0:
            self.hurt_cooldown -= dt

    def draw(self, r):
        # Body: cylinder
        model = mat4_mul(mat4_translate(self.pos[0], 0, self.pos[2]),
        mat4_scale(0.5, 1.4, 0.5))
        flash = 0
        if self.hit_flash > 0:
            flash = self.hit_flash / 0.2
        emissive = (flash, 0, 0)
        r.draw_cylinder(model, (0.2, 0.8, 0.2), emissive=emissive)
        # Head: smaller cylinder
        model2 = mat4_mul(mat4_translate(self.pos[0], 1.4, self.pos[2]),
        mat4_scale(0.35, 0.4, 0.35))
        r.draw_cylinder(model2, (0.9, 0.7, 0.5), emissive=emissive)
        # Barrel: small cube in front of player
        bx = self.pos[0] + math.cos(self.aim_angle) * 0.5
        bz = self.pos[2] + math.sin(self.aim_angle) * 0.5
        barrel_model = mat4_mul(mat4_mul(mat4_translate(bx, 1.0, bz),
        mat4_rotate_y(self.aim_angle)),
                                mat4_scale(0.6, 0.2, 0.2))
        r.draw_cube(barrel_model, (0.2, 0.2, 0.2))
        # Muzzle flash
        if self.muzzle_flash > 0:
            fx = self.pos[0] + math.cos(self.aim_angle) * 0.9
            fz = self.pos[2] + math.sin(self.aim_angle) * 0.9
            fm = mat4_mul(mat4_translate(fx, 1.0, fz), mat4_scale(0.3, 0.3, 0.3))
            r.draw_cube(fm, (1, 1, 0.5), emissive=(1, 0.8, 0.3))

# ============================================================
# Zombie
# ============================================================
class Zombie:
    def __init__(self, x, z, ztype='normal'):
        self.pos = np.array([x, 0.0, z], dtype=np.float32)
        self.ztype = ztype
        info = ZOMBIE_TYPES[ztype]
        self.hp = self.max_hp = info['hp']
        self.speed = info['speed']
        self.damage = info['damage']
        self.color = info['color']
        self.size = info['size']
        self.hit_flash = 0
        self.attack_cooldown = 0
        self.dying = False
        self.dying_time = 0
        self.dying_duration = 0.8
        self.dead = False
        self.wobble = random.uniform(0, 2*math.pi)

    def take_damage(self, amount):
        if self.dying:
            return False
        self.hp -= amount
        self.hit_flash = 0.15
        if self.hp <= 0:
            self.dying = True
            self.dying_time = 0
        return True

    def update(self, dt, game):
        if self.dying:
            self.dying_time += dt
            if self.dying_time >= self.dying_duration:
                self.dead = True
                # Drop loot
                game.on_zombie_killed(self)
            return

        # Move toward player
        dx = game.player.pos[0] - self.pos[0]
        dz = game.player.pos[2] - self.pos[2]
        dist = math.hypot(dx, dz)
        if dist > 0.1:
            dx /= dist; dz /= dist
            # Wobble for visual variety
            self.wobble += dt * 4
            perp_x, perp_z = -dz, dx
            wob = math.sin(self.wobble) * 0.15
            dx += perp_x * wob; dz += perp_z * wob
            mag = math.hypot(dx, dz)
            if mag > 0:
                dx /= mag; dz /= mag
            new_x = self.pos[0] + dx * self.speed * dt
            new_z = self.pos[2] + dz * self.speed * dt
            half_x = self.size[0] / 2
            half_z = self.size[2] / 2
            half = max(half_x, half_z)
            if not check_obstacle_collision(new_x, self.pos[2], half, game.obstacles, game.walls):
                self.pos[0] = new_x
            if not check_obstacle_collision(self.pos[0], new_z, half, game.obstacles, game.walls):
                self.pos[2] = new_z

        # Attack player
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        if dist < 1.5 and self.attack_cooldown <= 0:
            game.player.take_damage(self.damage, game)
            self.attack_cooldown = 1.0

        if self.hit_flash > 0:
            self.hit_flash -= dt

    def draw(self, r):
        sx, sy, sz = self.size
        flash = 0
        if self.hit_flash > 0:
            flash = self.hit_flash / 0.15
        emissive = (flash * 1.0, 0, 0)

        if self.dying:
            progress = self.dying_time / self.dying_duration
            angle = progress * (math.pi / 2)
            sink = progress * 0.5
            alpha = max(0, 1.0 - progress * 0.5)
            model = mat4_mul(mat4_mul(mat4_mul(
                mat4_translate(self.pos[0], -sink + sy/2, self.pos[2]),
                mat4_rotate_x(angle)),
                mat4_scale(sx, sy, sz)),
                mat4_translate(0, -0.5, 0))
            r.draw_cube(model, self.color, emissive=emissive, alpha=alpha)
        else:
            model = mat4_mul(mat4_translate(self.pos[0], sy/2, self.pos[2]),
            mat4_scale(sx, sy, sz))
            r.draw_cube(model, self.color, emissive=emissive)
            # Head
            head_model = mat4_mul(mat4_translate(self.pos[0], sy + 0.15, self.pos[2]),
            mat4_scale(sx*0.6, 0.3, sz*0.6))
            r.draw_cube(head_model, (self.color[0]*1.2, self.color[1]*1.2, self.color[2]*1.2))

# ============================================================
# Bullet
# ============================================================
class Bullet:
    def __init__(self, pos, vel, damage, color, owner='player'):
        self.pos = np.array(pos, dtype=np.float32)
        self.vel = np.array(vel, dtype=np.float32)
        self.damage = damage
        self.color = color
        self.owner = owner
        self.life = 2.0
        self.dead = False

    def update(self, dt, game):
        steps = 4
        sub_dt = dt / steps
        for _ in range(steps):
            self.pos += self.vel * sub_dt
            self.life -= sub_dt
            if self.life <= 0:
                self.dead = True
                return
            # Check out of bounds
            if abs(self.pos[0]) > WORLD_HALF or abs(self.pos[2]) > WORLD_HALF:
                self.dead = True
                return
            # Check obstacle collision
            if check_obstacle_collision(self.pos[0], self.pos[2], 0.05, game.obstacles, game.walls):
                # Spawn spark particles
                for _ in range(4):
                    game.particles.append(Particle(self.pos[:], (1, 0.7, 0.2)))
                self.dead = True
                return
            # Check zombie collision
            for z in game.zombies:
                if z.dying:
                    continue
                zx, zz = z.pos[0], z.pos[2]
                if abs(self.pos[0] - zx) < z.size[0]/2 + 0.1 and abs(self.pos[2] - zz) < z.size[2]/2 + 0.1:
                    hit = z.take_damage(self.damage)
                    if hit:
                        game.add_feedback(str(int(self.damage)), z.pos[:], (1, 0.2, 0.2), vy=2.0)
                        # Hit sparks
                        for _ in range(8):
                            game.particles.append(Particle(self.pos[:], (1, 0.6, 0.2)))
                        game.play_sound('hit')
                    self.dead = True
                    return

    def draw(self, r):
        model = mat4_mul(mat4_translate(self.pos[0], self.pos[1], self.pos[2]),
        mat4_scale(0.12, 0.12, 0.3))
        model = mat4_mul(model, mat4_rotate_y(math.atan2(self.vel[2], self.vel[0])))
        r.draw_cube(model, self.color, emissive=(0.6, 0.5, 0.2))

# ============================================================
# Loot Item
# ============================================================
LOOT_COLORS = {
    'ammo_pistol': (1, 1, 0),
    'ammo_shotgun': (1, 0.7, 0),
    'ammo_rifle': (0.7, 1, 0.3),
    'medkit': (1, 0.2, 0.2),
    'weapon_shotgun': (0.2, 0.5, 1),
    'weapon_rifle': (0.3, 0.7, 1),
}

class LootItem:
    def __init__(self, x, z, ltype):
        self.pos = np.array([x, 0.3, z], dtype=np.float32)
        self.type = ltype
        self.color = LOOT_COLORS.get(ltype, (1, 1, 1))
        self.bob = random.uniform(0, 2*math.pi)
        self.picked = False
        self.life = 60.0  # despawn after 60s

    def update(self, dt, game):
        self.bob += dt * 3
        self.life -= dt
        if self.life <= 0:
            self.picked = True
            return
        # Auto pickup
        dx = game.player.pos[0] - self.pos[0]
        dz = game.player.pos[2] - self.pos[2]
        if dx*dx + dz*dz < 1.5*1.5:
            if game.player.pickup_loot(self, game):
                self.picked = True

    def draw(self, r):
        y = 0.3 + math.sin(self.bob) * 0.15
        # Glow emissive
        emissive = (self.color[0]*0.5, self.color[1]*0.5, self.color[2]*0.5)
        model = mat4_mul(mat4_translate(self.pos[0], y, self.pos[2]),
        mat4_scale(0.4, 0.4, 0.4))
        r.draw_cube(model, self.color, emissive=emissive)
        # Ring on ground
        ring_model = mat4_mul(mat4_translate(self.pos[0], 0.02, self.pos[2]),
        mat4_scale(0.7, 1, 0.7))
        r.draw_quad(ring_model, self.color, emissive=emissive, alpha=0.5)

# ============================================================
# Particle
# ============================================================
class Particle:
    def __init__(self, pos, color, speed=3.0):
        self.pos = np.array(pos, dtype=np.float32)
        angle = random.uniform(0, 2*math.pi)
        elev = random.uniform(0.5, 2.0)
        self.vel = np.array([math.cos(angle)*speed, elev*speed, math.sin(angle)*speed], dtype=np.float32)
        self.color = color
        self.life = 0.5
        self.max_life = 0.5
        self.size = random.uniform(0.05, 0.15)
        self.dead = False

    def update(self, dt):
        self.pos += self.vel * dt
        self.vel[1] -= 9.8 * dt  # gravity
        if self.pos[1] < 0:
            self.pos[1] = 0
            self.vel[1] = 0
            self.vel[0] *= 0.5
            self.vel[2] *= 0.5
        self.life -= dt
        if self.life <= 0:
            self.dead = True

    def draw(self, r):
        alpha = max(0, self.life / self.max_life)
        model = mat4_mul(mat4_translate(self.pos[0], self.pos[1], self.pos[2]),
        mat4_scale(self.size, self.size, self.size))
        r.draw_cube(model, self.color, emissive=self.color, alpha=alpha)

# ============================================================
# Wave Manager
# ============================================================
class WaveManager:
    def __init__(self):
        self.wave = 0
        self.to_spawn = 0
        self.spawn_timer = 0
        self.spawn_interval = 1.0
        self.between_waves = True
        self.countdown = 5.0
        self.kills_this_wave = 0

    def update(self, dt, game):
        if self.between_waves:
            self.countdown -= dt
            if self.countdown <= 0:
                self._start_wave(game)
        else:
            if self.to_spawn > 0:
                self.spawn_timer -= dt
                if self.spawn_timer <= 0:
                    self._spawn_zombie(game)
                    self.to_spawn -= 1
                    self.spawn_timer = self.spawn_interval
            else:
                if len(game.zombies) == 0:
                    self.between_waves = True
                    self.countdown = 10.0
                    # Give player a small reward
                    game.player.ammo['pistol'] += 10
                    game.add_feedback("Wave Cleared! +10 Pistol Ammo", game.player.pos[:], (0, 1, 0))

    def _start_wave(self, game):
        self.wave += 1
        self.kills_this_wave = 0
        count = int(5 * (1.2 ** (self.wave - 1))) + self.wave
        self.to_spawn = count
        self.between_waves = False
        self.spawn_timer = 0
        self.spawn_interval = max(0.2, 1.0 - self.wave * 0.05)

    def _spawn_zombie(self, game):
        # Spawn outside player's view
        angle = random.uniform(0, 2*math.pi)
        dist = random.uniform(22, 30)
        x = game.player.pos[0] + math.cos(angle) * dist
        z = game.player.pos[2] + math.sin(angle) * dist
        x = max(-WORLD_HALF+2, min(WORLD_HALF-2, x))
        z = max(-WORLD_HALF+2, min(WORLD_HALF-2, z))
        # Choose type
        r = random.random()
        if self.wave >= 3 and r < 0.15:
            t = 'tank'
        elif self.wave >= 2 and r < 0.40:
            t = 'fast'
        else:
            t = 'normal'
        game.zombies.append(Zombie(x, z, t))

# ============================================================
# HUD
# ============================================================
class HUD:
    def draw(self, r, text, game):
        r.begin_hud()
        # Health bar (bottom left)
        x, y, w, h = 20, SCREEN_H - 50, 200, 20
        r.draw_hud_quad(x, y, w, h, (0.2, 0, 0))
        hp_w = w * (game.player.hp / game.player.MAX_HP)
        r.draw_hud_quad(x, y, hp_w, h, (0.8, 0.1, 0.1))
        r.draw_hud_quad(x-2, y-2, w+4, h+4, (0, 0, 0), alpha=0.0)  # spacer
        r.draw_text(text, "HP", x + 5, y + 2, 'small', (255, 255, 255))
        r.draw_text(text, f"{int(game.player.hp)}/{game.player.MAX_HP}", x + w - 50, y + 2, 'small', (255, 255, 255))

        # Stamina bar
        y2 = y - 25
        r.draw_hud_quad(x, y2, w, h, (0.2, 0.2, 0))
        st_w = w * (game.player.stamina / game.player.MAX_STAMINA)
        r.draw_hud_quad(x, y2, st_w, h, (0.9, 0.8, 0.1))
        r.draw_text(text, "STA", x + 5, y2 + 2, 'small', (255, 255, 255))

        # Weapon info
        y3 = y2 - 60
        wkey = game.player.current_weapon_key
        if wkey:
            w = WEAPONS[wkey]
            r.draw_text(text, w['name'], x, y3, 'med', (255, 255, 255))
            ammo_str = f"{game.player.magazine[wkey]} / {game.player.ammo[wkey]}"
            r.draw_text(text, ammo_str, x, y3 + 28, 'small', (255, 220, 100))
            if game.player.reloading:
                r.draw_text(text, "RELOADING...", x, y3 + 50, 'small', (255, 100, 100))
        # Medkits
        r.draw_text(text, f"Medkits: {game.player.consumables} (F)", x, y3 + 75, 'small', (255, 100, 100))

        # Wave info (top left)
        r.draw_text(text, f"Wave: {game.wave_mgr.wave}", 20, 20, 'med', (255, 255, 255))
        r.draw_text(text, f"Zombies: {len(game.zombies)}", 20, 50, 'small', (255, 100, 100))
        r.draw_text(text, f"Score: {game.score}", 20, 75, 'small', (255, 220, 100))
        r.draw_text(text, f"Kills: {game.total_kills}", 20, 100, 'small', (200, 200, 200))

        # Inventory (top right)
        for i in range(3):
            slot_x = SCREEN_W - 200 + i * 60
            slot_y = 20
            slot_w, slot_h = 50, 50
            wkey = game.player.weapons[i]
            color = (0.3, 0.3, 0.3) if wkey is None else WEAPONS[wkey]['color']
            r.draw_hud_quad(slot_x, slot_y, slot_w, slot_h, (0.1, 0.1, 0.1))
            r.draw_hud_quad(slot_x + 4, slot_y + 4, slot_w - 8, slot_h - 8, color)
            if i == game.player.current_weapon:
                r.draw_hud_quad(slot_x - 2, slot_y - 2, slot_w + 4, slot_h + 4, (1, 1, 1), alpha=0.3)
            r.draw_text(text, str(i+1), slot_x + 5, slot_y + slot_h + 5, 'small', (255, 255, 255))
            if wkey:
                r.draw_text(text, WEAPONS[wkey]['name'][:3], slot_x + 5, slot_y + 5, 'tiny', (255, 255, 255))

        # Wave countdown (center bottom)
        if game.wave_mgr.between_waves:
            cd = max(0, game.wave_mgr.countdown)
            txt = f"Next Wave in {cd:.1f}s" if game.wave_mgr.wave > 0 else f"First Wave in {cd:.1f}s"
            r.draw_text(text, txt, SCREEN_W // 2, SCREEN_H - 100, 'large', (255, 220, 100), center=True)
        else:
            r.draw_text(text, f"Wave {game.wave_mgr.wave} - {len(game.zombies)} zombies left",
                        SCREEN_W // 2, SCREEN_H - 60, 'med', (255, 255, 255), center=True)

        # Crosshair
        mx, my = pygame.mouse.get_pos()
        r.draw_hud_quad(mx - 1, my - 8, 2, 16, (1, 1, 1))
        r.draw_hud_quad(mx - 8, my - 1, 16, 2, (1, 1, 1))

        # Feedback texts
        for f in game.feedback_texts:
            wx, wy, wz = f['pos']
            # Project to screen (approximate)
            sx, sy = self._world_to_screen(wx, wy, wz, game)
            alpha = min(1.0, f['life'] * 2)
            r.draw_text(text, f['text'], int(sx), int(sy), 'small', f['color_rgb'], alpha=alpha, center=True)

        r.end_hud()

    def _world_to_screen(self, wx, wy, wz, game):
        # Project world point to screen using view and proj
        vp = mat4_mul(game.proj_matrix, game.view_matrix)
        world = np.array([wx, wy, wz, 1], dtype=np.float32)
        clip = vp.dot(world)
        if clip[3] == 0:
            return 0, 0
        ndc = clip[:3] / clip[3]
        sx = (ndc[0] + 1) * 0.5 * SCREEN_W
        sy = (1 - ndc[1]) * 0.5 * SCREEN_H
        return sx, sy

# ============================================================
# Game
# ============================================================
class Game:
    def __init__(self):
        random.seed()
        pygame.init()
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
        
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.set_caption("3D Top-Down Zombie Looter Shooter")
        
        self.renderer = Renderer(SCREEN_W, SCREEN_H)
        self.renderer.text_cache = TextRenderer()
        self.text = self.renderer.text_cache
        
        # Sound
        self.sound_ok = False
        self.sounds = {}
        try:
            mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.sound_ok = True
            self._make_sounds()
        except Exception:
            self.sound_ok = False

        self.clock = pygame.time.Clock()
        self.running = True
        self.state = STATE_MENU
        self.menu_option = 0
        
        self.player = None
        self.zombies = []
        self.bullets = []
        self.loot = []
        self.particles = []
        self.decals = []
        self.obstacles = []
        self.walls = []
        self.feedback_texts = []
        self.wave_mgr = None
        self.score = 0
        self.total_kills = 0
        self.shake_time = 0
        self.shake_intensity = 0
        self.shake_offset = (0, 0)
        self.mouse_world = np.array([0, 0, 0], dtype=np.float32)
        self.view_matrix = mat4_identity()
        self.proj_matrix = mat4_identity()

    def _make_sounds(self):
        sr = 22050
        def make(freq, dur, vol=0.3, decay=5.0, noise=0.0, sweep=0.0):
            n = int(sr * dur)
            t = np.linspace(0, dur, n, False)
            env = np.exp(-t * decay)
            f = freq + sweep * t
            wave = np.sin(2 * np.pi * f * t) * env * vol
            if noise > 0:
                wave += np.random.uniform(-1, 1, n) * env * vol * noise
            stereo = np.column_stack([wave, wave])
            return mixer.Sound((stereo * 32767).astype(np.int16))
        self.sounds['shoot_pistol'] = make(800, 0.08, 0.2, 25)
        self.sounds['shoot_shotgun'] = make(300, 0.15, 0.3, 12, noise=0.5)
        self.sounds['shoot_rifle'] = make(1200, 0.06, 0.2, 30)
        self.sounds['hit'] = make(200, 0.1, 0.2, 15, noise=0.3)
        self.sounds['reload'] = make(400, 0.1, 0.15, 10)
        self.sounds['hurt'] = make(150, 0.3, 0.3, 5, noise=0.3)
        self.sounds['pickup'] = make(600, 0.15, 0.2, 8, sweep=800)
        self.sounds['empty'] = make(200, 0.05, 0.1, 30)
        self.sounds['zombie_die'] = make(100, 0.4, 0.2, 4, sweep=-50)

    def play_sound(self, name):
        if self.sound_ok and name in self.sounds:
            self.sounds[name].play()

    def shake(self, duration, intensity):
        self.shake_time = duration
        self.shake_intensity = intensity

    def add_feedback(self, text, pos, color, vy=1.5):
        self.feedback_texts.append({
            'text': text,
            'pos': np.array(pos, dtype=np.float32),
            'life': 1.2,
            'max_life': 1.2,
            'vy': vy,
            'color_rgb': tuple(int(c*255) for c in color),
        })

    def on_zombie_killed(self, zombie):
        self.score += {'normal': 10, 'fast': 15, 'tank': 30}.get(zombie.ztype, 10)
        self.total_kills += 1
        # Blood decal
        self.decals.append({
            'x': zombie.pos[0], 'z': zombie.pos[2],
            'size': random.uniform(1.0, 1.8),
            'rot': random.uniform(0, math.pi),
            'life': 999,
        })
        if len(self.decals) > 50:
            self.decals.pop(0)
        # Loot drop
        self._drop_loot(zombie.pos[0], zombie.pos[2], zombie.ztype)
        # Particles
        for _ in range(12):
            self.particles.append(Particle([zombie.pos[0], 0.5, zombie.pos[2]], (0.6, 0.05, 0.05), speed=4.0))
        self.play_sound('zombie_die')

    def _drop_loot(self, x, z, ztype):
        # Loot probability table
        rolls = 1 if ztype != 'tank' else 2
        for _ in range(rolls):
            r = random.random()
            if r < 0.40:
                # Ammo
                ammo_types = ['ammo_pistol', 'ammo_shotgun', 'ammo_rifle']
                weights = [0.5, 0.25, 0.25]
                choice = random.choices(ammo_types, weights=weights)[0]
                self.loot.append(LootItem(x + random.uniform(-0.5, 0.5),
                z + random.uniform(-0.5, 0.5), choice))
            elif r < 0.55:
                self.loot.append(LootItem(x, z, 'medkit'))
            elif r < 0.65:
                # Weapon drops
                if not self.player.weapons[1]:
                    self.loot.append(LootItem(x, z, 'weapon_shotgun'))
                elif not self.player.weapons[2]:
                    self.loot.append(LootItem(x, z, 'weapon_rifle'))
                else:
                    self.loot.append(LootItem(x, z, 'ammo_rifle'))
            # else: no drop

    def start_game(self):
        self.player = Player()
        self.zombies = []
        self.bullets = []
        self.loot = []
        self.particles = []
        self.decals = []
        self.feedback_texts = []
        self.score = 0
        self.total_kills = 0
        self._generate_map()
        self.wave_mgr = WaveManager()
        self.state = STATE_PLAYING

    def _generate_map(self):
        self.obstacles = []
        for _ in range(25):
            x = random.uniform(-WORLD_HALF*0.85, WORLD_HALF*0.85)
            z = random.uniform(-WORLD_HALF*0.85, WORLD_HALF*0.85)
            if math.hypot(x, z) < 10:
                continue
            w = random.uniform(2, 5)
            d = random.uniform(2, 5)
            h = random.uniform(2, 6)
            self.obstacles.append({'x': x, 'z': z, 'w': w, 'd': d, 'h': h})
        t = 1.0
        s = WORLD_HALF
        self.walls = [
            {'x': 0, 'z': s+t/2, 'w': s*2+t*2, 'd': t, 'h': 3},
            {'x': 0, 'z': -s-t/2, 'w': s*2+t*2, 'd': t, 'h': 3},
            {'x': s+t/2, 'z': 0, 'w': t, 'd': s*2+t*2, 'h': 3},
            {'x': -s-t/2, 'z': 0, 'w': t, 'd': s*2+t*2, 'h': 3},
        ]

    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 1/30)
            self._handle_events()
            if self.state == STATE_PLAYING:
                self._update(dt)
            self._render()
            pygame.display.flip()
        pygame.quit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_PLAYING:
                        self.state = STATE_PAUSED
                    elif self.state == STATE_PAUSED:
                        self.state = STATE_PLAYING
                    elif self.state == STATE_MENU:
                        self.running = False
                    elif self.state == STATE_GAME_OVER:
                        self.state = STATE_MENU
                elif self.state == STATE_MENU:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.menu_option = (self.menu_option - 1) % 2
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.menu_option = (self.menu_option + 1) % 2
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if self.menu_option == 0:
                            self.start_game()
                        else:
                            self.running = False
                elif self.state == STATE_PLAYING:
                    if event.key == pygame.K_r:
                        self.player.reload(self)
                    elif event.key == pygame.K_1:
                        self.player.switch_weapon(0)
                    elif event.key == pygame.K_2:
                        self.player.switch_weapon(1)
                    elif event.key == pygame.K_3:
                        self.player.switch_weapon(2)
                    elif event.key == pygame.K_f:
                        self.player.use_medkit(self)
                elif self.state == STATE_GAME_OVER:
                    if event.key == pygame.K_r:
                        self.start_game()
                elif self.state == STATE_PAUSED:
                    if event.key == pygame.K_r:
                        self.start_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == STATE_PLAYING:
                    if event.button == 1:
                        self.player.try_shoot(self)

    def _update(self, dt):
        keys = pygame.key.get_pressed()
        mx, my = pygame.mouse.get_pos()
        self._update_mouse_world(mx, my)
        self.player.update(dt, self, keys)
        self.wave_mgr.update(dt, self)
        
        for z in self.zombies[:]:
            z.update(dt, self)
            if z.dead:
                self.zombies.remove(z)
        
        for b in self.bullets[:]:
            b.update(dt, self)
            if b.dead:
                self.bullets.remove(b)
        
        for l in self.loot[:]:
            l.update(dt, self)
            if l.picked:
                self.loot.remove(l)
        
        for p in self.particles[:]:
            p.update(dt)
            if p.dead:
                self.particles.remove(p)
        
        for f in self.feedback_texts[:]:
            f['life'] -= dt
            f['pos'][1] += f['vy'] * dt
            if f['life'] <= 0:
                self.feedback_texts.remove(f)
        
        if self.shake_time > 0:
            self.shake_time -= dt
            intensity = max(0, self.shake_time / 0.3) * self.shake_intensity
            self.shake_offset = (random.uniform(-1, 1) * intensity,
                                 random.uniform(-1, 1) * intensity)
        else:
            self.shake_offset = (0, 0)
        
        if self.player.hp <= 0:
            self.state = STATE_GAME_OVER

    def _update_mouse_world(self, mx, my):
        view = self._get_view_matrix()
        proj = self._get_proj_matrix()
        try:
            inv_vp = np.linalg.inv(np.dot(proj, view))
        except np.linalg.LinAlgError:
            return
        nx = 2.0 * mx / SCREEN_W - 1.0
        ny = 1.0 - 2.0 * my / SCREEN_H
        near = np.dot(inv_vp, np.array([nx, ny, -1, 1], dtype=np.float32))
        far = np.dot(inv_vp, np.array([nx, ny, 1, 1], dtype=np.float32))
        if abs(near[3]) > 1e-6:
            near = near[:3] / near[3]
        else:
            near = near[:3]
        if abs(far[3]) > 1e-6:
            far = far[:3] / far[3]
        else:
            far = far[:3]
        if abs(far[1] - near[1]) < 1e-6:
            return
        t = -near[1] / (far[1] - near[1])
        self.mouse_world = (near + t * (far - near)).astype(np.float32)

    def _get_view_matrix(self):
        if not self.player:
            return mat4_look_at([0, 30, 20], [0, 0, 0], [0, 1, 0])
        px, _, pz = self.player.pos
        ox, oz = self.shake_offset
        return mat4_look_at([px+ox, 30, pz+20+oz], [px+ox, 0, pz+oz], [0, 1, 0])

    def _get_proj_matrix(self):
        aspect = SCREEN_W / SCREEN_H
        size = 18
        return mat4_ortho(-size*aspect, size*aspect, -size, size, 0.1, 200)

    def _render(self):
        glClearColor(0.05, 0.05, 0.08, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        if self.state in (STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER):
            self._render_3d()
            self._render_hud()
        
        if self.state == STATE_MENU:
            self._render_menu()
        elif self.state == STATE_PAUSED:
            self._render_pause()
        elif self.state == STATE_GAME_OVER:
            self._render_game_over()

    def _render_3d(self):
        self.view_matrix = self._get_view_matrix()
        self.proj_matrix = self._get_proj_matrix()
        view_pos = [self.player.pos[0] + self.shake_offset[0], 30,
                    self.player.pos[2] + 20 + self.shake_offset[1]]
        self.renderer.begin_3d(self.view_matrix, self.proj_matrix, view_pos, self.player.pos)
        
        # Ground
        ground_model = mat4_scale(WORLD_HALF*2, 1, WORLD_HALF*2)
        self.renderer.draw_quad(ground_model, (0.25, 0.25, 0.25))
        
        # Grid lines for visual reference (use small quads)
        for i in range(-5, 6):
            x = i * 10
            # X grid line
            m = mat4_mul(mat4_translate(x, 0.01, 0), mat4_scale(0.05, 1, WORLD_HALF*2))
            self.renderer.draw_quad(m, (0.3, 0.3, 0.3), alpha=0.5)
            # Z grid line
            m = mat4_mul(mat4_translate(0, 0.01, x), mat4_scale(WORLD_HALF*2, 1, 0.05))
            self.renderer.draw_quad(m, (0.3, 0.3, 0.3), alpha=0.5)
        
        # Blood decals
        for d in self.decals:
            m = mat4_mul(mat4_mul(mat4_translate(d['x'], 0.02, d['z']),
                                   mat4_rotate_y(d['rot'])),
                         mat4_scale(d['size'], 1, d['size']))
            self.renderer.draw_quad(m, (0.5, 0.05, 0.05), alpha=0.7)
        
        # Obstacles
        for obs in self.obstacles:
            m = mat4_mul(mat4_translate(obs['x'], obs['h']/2, obs['z']),
                         mat4_scale(obs['w'], obs['h'], obs['d']))
            self.renderer.draw_cube(m, (0.5, 0.4, 0.3))
        
        # Walls
        for w in self.walls:
            m = mat4_mul(mat4_translate(w['x'], w['h']/2, w['z']),
                         mat4_scale(w['w'], w['h'], w['d']))
            self.renderer.draw_cube(m, (0.2, 0.2, 0.25))
        
        # Loot
        for l in self.loot:
            l.draw(self.renderer)
        
        # Particles
        for p in self.particles:
            p.draw(self.renderer)
        
        # Bullets
        for b in self.bullets:
            b.draw(self.renderer)
        
        # Zombies
        for z in self.zombies:
            z.draw(self.renderer)
        
        # Player
        self.player.draw(self.renderer)

    def _render_hud(self):
        HUD().draw(self.renderer, self.text, self)

    def _render_menu(self):
        self.renderer.begin_hud()
        r = self.renderer
        # Background
        r.draw_hud_quad(0, 0, SCREEN_W, SCREEN_H, (0.05, 0.05, 0.1))
        r.draw_text(self.text, "3D ZOMBIE LOOTER SHOOTER", SCREEN_W//2, 150, 'huge', (200, 50, 50), center=True)
        r.draw_text(self.text, "Survive the endless waves", SCREEN_W//2, 240, 'med', (200, 200, 200), center=True)
        
        options = ["New Game", "Quit"]
        for i, opt in enumerate(options):
            color = (255, 220, 100) if i == self.menu_option else (200, 200, 200)
            r.draw_text(self.text, opt, SCREEN_W//2, 400 + i*60, 'large', color, center=True)
        
        r.draw_text(self.text, "WASD: Move | Mouse: Aim | LMB: Shoot | R: Reload | Shift: Sprint | F: Medkit | 1-3: Weapons", SCREEN_W//2, SCREEN_H - 50, 'small', (180, 180, 180), center=True)
        r.draw_text(self.text, "ESC: Pause | Up/Down: Navigate | Enter: Select", SCREEN_W//2, SCREEN_H - 25, 'small', (180, 180, 180), center=True)
        self.renderer.end_hud()

    def _render_pause(self):
        self.renderer.begin_hud()
        r = self.renderer
        r.draw_hud_quad(0, 0, SCREEN_W, SCREEN_H, (0, 0, 0), alpha=0.6)
        r.draw_text(self.text, "PAUSED", SCREEN_W//2, 200, 'huge', (255, 220, 100), center=True)
        r.draw_text(self.text, "ESC: Resume", SCREEN_W//2, 350, 'med', (255, 255, 255), center=True)
        r.draw_text(self.text, "R: Restart", SCREEN_W//2, 400, 'med', (255, 255, 255), center=True)
        r.draw_text(self.text, "Close window to Quit", SCREEN_W//2, 450, 'med', (255, 255, 255), center=True)
        self.renderer.end_hud()

    def _render_game_over(self):
        self.renderer.begin_hud()
        r = self.renderer
        r.draw_hud_quad(0, 0, SCREEN_W, SCREEN_H, (0.2, 0, 0), alpha=0.7)
        r.draw_text(self.text, "GAME OVER", SCREEN_W//2, 180, 'huge', (255, 50, 50), center=True)
        r.draw_text(self.text, f"Score: {self.score}", SCREEN_W//2, 320, 'large', (255, 220, 100), center=True)
        r.draw_text(self.text, f"Wave Reached: {self.wave_mgr.wave}", SCREEN_W//2, 380, 'large', (255, 220, 100), center=True)
        r.draw_text(self.text, f"Total Kills: {self.total_kills}", SCREEN_W//2, 440, 'med', (255, 255, 255), center=True)
        r.draw_text(self.text, "R: Restart | ESC: Main Menu", SCREEN_W//2, 530, 'med', (255, 255, 255), center=True)
        self.renderer.end_hud()

# ============================================================
# Main
# ============================================================
if __name__ == '__main__':
    Game().run()