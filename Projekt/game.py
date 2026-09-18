from __future__ import annotations

import math
import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pygame
from pygame import mixer
from OpenGL.GL import *

from Projekt.scripts.spawn_manager import SpawnManager
from Projekt.systems.spawn_system import WaveManager
from Projekt.entities.world_object import Particle
from Projekt.entities.loot import LootItem
from Projekt.entities.player import Player as ModularPlayer
from Projekt.entities.enemy import Enemy as ModularEnemy
from Projekt.ui.hud import GameHUD
from Projekt.ui.overlays import GameOverlays
from Projekt.systems.render_system import (
    mat4_identity,
    mat4_translate,
    mat4_scale,
    mat4_rotate_y,
    mat4_rotate_x,
    mat4_ortho,
    mat4_look_at,
    mat4_mul,
    TextRenderer,
    GameRenderer,
)
from Projekt.systems.combat_system import is_position_blocked
from Projekt.scripts.world_builder import WorldBuilder
from Projekt.systems.game_state import FeedbackSystem, ScreenShake

try:
    import settings
except ModuleNotFoundError:
    from Projekt import settings


SCREEN_W, SCREEN_H = 1200, 800
FPS = 120
WORLD_HALF = settings.WORLD_HALF

STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER = 0, 1, 2, 3

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

check_obstacle_collision = is_position_blocked


class Game:
    world_half = WORLD_HALF

    def __init__(self):
        self.screen_width = SCREEN_W
        self.screen_height = SCREEN_H
        random.seed()
        pygame.init()
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)

        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.set_caption("3D Top-Down Zombie Looter Shooter")

        self.renderer = GameRenderer(SCREEN_W, SCREEN_H)
        self.text = TextRenderer()
        self.overlays = GameOverlays(SCREEN_W, SCREEN_H)

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
        self.feedback_system = FeedbackSystem()
        self.screen_shake = ScreenShake()
        self.wave_mgr = None
        self.spawn_manager = SpawnManager(fallback_center=(0.0, 0.0))
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

        self.sounds["shoot_pistol"] = make(800, 0.08, 0.2, 25)
        self.sounds["shoot_shotgun"] = make(300, 0.15, 0.3, 12, noise=0.5)
        self.sounds["shoot_rifle"] = make(1200, 0.06, 0.2, 30)
        self.sounds["hit"] = make(200, 0.1, 0.2, 15, noise=0.3)
        self.sounds["reload"] = make(400, 0.1, 0.15, 10)
        self.sounds["hurt"] = make(150, 0.3, 0.3, 5, noise=0.3)
        self.sounds["pickup"] = make(600, 0.15, 0.2, 8, sweep=800)
        self.sounds["empty"] = make(200, 0.05, 0.1, 30)
        self.sounds["zombie_die"] = make(100, 0.4, 0.2, 4, sweep=-50)

    def play_sound(self, name):
        if self.sound_ok and name in self.sounds:
            self.sounds[name].play()

    def shake(self, duration, intensity):
        self.screen_shake.trigger(duration, intensity)
        self.shake_time = duration
        self.shake_intensity = intensity

    def add_feedback(self, text, pos, color, vy=1.5):
        self.feedback_system.add(text, pos, color, vy)
        self.feedback_texts = self.feedback_system.items

    def is_position_blocked(self, x, z, radius):
        return check_obstacle_collision(x, z, radius, self.obstacles, self.walls)

    def on_zombie_killed(self, zombie):
        self.score += {"normal": 10, "fast": 15, "tank": 30}.get(zombie.ztype, 10)
        self.total_kills += 1
        self.decals.append({
            "x": zombie.pos[0],
            "z": zombie.pos[2],
            "size": random.uniform(1.0, 1.8),
            "rot": random.uniform(0, math.pi),
            "life": 999,
        })
        if len(self.decals) > 50:
            self.decals.pop(0)
        self._drop_loot(zombie.pos[0], zombie.pos[2], zombie.ztype)
        for _ in range(12):
            self.particles.append(Particle([zombie.pos[0], 0.5, zombie.pos[2]], (0.6, 0.05, 0.05), speed=4.0))
        self.play_sound("zombie_die")

    def _drop_loot(self, x, z, ztype):
        rolls = 1 if ztype != "tank" else 2
        for _ in range(rolls):
            r = random.random()
            if r < 0.40:
                ammo_types = ["ammo_pistol", "ammo_shotgun", "ammo_rifle"]
                weights = [0.5, 0.25, 0.25]
                choice = random.choices(ammo_types, weights=weights)[0]
                self.loot.append(LootItem(x + random.uniform(-0.5, 0.5), z + random.uniform(-0.5, 0.5), choice))
            elif r < 0.55:
                self.loot.append(LootItem(x, z, "medkit"))
            elif r < 0.65:
                if not self.player.weapons[1]:
                    self.loot.append(LootItem(x, z, "weapon_shotgun"))
                elif not self.player.weapons[2]:
                    self.loot.append(LootItem(x, z, "weapon_rifle"))
                else:
                    self.loot.append(LootItem(x, z, "ammo_rifle"))

    def start_game(self):
        self.player = ModularPlayer()
        self.zombies = []
        self.bullets = []
        self.loot = []
        self.particles = []
        self.decals = []
        self.feedback_texts = []
        self.feedback_system = FeedbackSystem()
        self.screen_shake = ScreenShake()
        self.score = 0
        self.total_kills = 0
        self._generate_map()
        self.wave_mgr = WaveManager(ModularEnemy, self.spawn_manager)
        self.state = STATE_PLAYING

    def _generate_map(self):
        self.obstacles, self.walls = WorldBuilder(WORLD_HALF).build_arena()

    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 1 / 30)
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
                if self.state == STATE_PLAYING and event.button == 1:
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

        self.feedback_system.update(dt)

        self.shake_offset = self.screen_shake.update(dt)

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
        return mat4_look_at([px + ox, 30, pz + 20 + oz], [px + ox, 0, pz + oz], [0, 1, 0])

    def _get_proj_matrix(self):
        aspect = SCREEN_W / SCREEN_H
        size = 18
        return mat4_ortho(-size * aspect, size * aspect, -size, size, 0.1, 200)

    def _render(self):
        glClearColor(0.05, 0.05, 0.08, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if self.state in (STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER):
            self._render_3d()
            self._render_hud()

        if self.state == STATE_MENU:
            self.overlays.draw_menu(self.renderer, self.text, self.menu_option)
        elif self.state == STATE_PAUSED:
            self.overlays.draw_pause(self.renderer, self.text)
        elif self.state == STATE_GAME_OVER:
            self.overlays.draw_game_over(self.renderer, self.text, self.score, self.wave_mgr.wave, self.total_kills)

    def _render_3d(self):
        self.view_matrix = self._get_view_matrix()
        self.proj_matrix = self._get_proj_matrix()
        view_pos = [self.player.pos[0] + self.shake_offset[0], 30, self.player.pos[2] + 20 + self.shake_offset[1]]
        self.renderer.begin_3d(self.view_matrix, self.proj_matrix, view_pos, self.player.pos)

        ground_model = mat4_scale(WORLD_HALF * 2, 1, WORLD_HALF * 2)
        self.renderer.draw_quad(ground_model, (0.25, 0.25, 0.25))

        for i in range(-5, 6):
            x = i * 10
            m = mat4_mul(mat4_translate(x, 0.01, 0), mat4_scale(0.05, 1, WORLD_HALF * 2))
            self.renderer.draw_quad(m, (0.3, 0.3, 0.3), alpha=0.5)
            m = mat4_mul(mat4_translate(0, 0.01, x), mat4_scale(WORLD_HALF * 2, 1, 0.05))
            self.renderer.draw_quad(m, (0.3, 0.3, 0.3), alpha=0.5)

        for d in self.decals:
            m = mat4_mul(mat4_mul(mat4_translate(d["x"], 0.02, d["z"]), mat4_rotate_y(d["rot"])), mat4_scale(d["size"], 1, d["size"]))
            self.renderer.draw_quad(m, (0.5, 0.05, 0.05), alpha=0.7)

        for obs in self.obstacles:
            m = mat4_mul(mat4_translate(obs["x"], obs["h"] / 2, obs["z"]), mat4_scale(obs["w"], obs["h"], obs["d"]))
            self.renderer.draw_cube(m, (0.5, 0.4, 0.3))

        for w in self.walls:
            m = mat4_mul(mat4_translate(w["x"], w["h"] / 2, w["z"]), mat4_scale(w["w"], w["h"], w["d"]))
            self.renderer.draw_cube(m, (0.2, 0.2, 0.25))

        for l in self.loot:
            l.draw(self.renderer)

        for p in self.particles:
            p.draw(self.renderer)

        for b in self.bullets:
            b.draw(self.renderer)

        for z in self.zombies:
            z.draw(self.renderer)

        self.player.draw(self.renderer)

    def _render_hud(self):
        GameHUD().draw(self.renderer, self.text, self)

def main() -> None:
    Game().run()


if __name__ == "__main__":
    main()
