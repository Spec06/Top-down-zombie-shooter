"""A very small particle system for hit effects using OpenGL points."""
import random
import math
from OpenGL.GL import glBegin, glEnd, glVertex3f, glColor4f, glPointSize, GL_POINTS


class Particle:
    def __init__(self, pos, vel, color=(1.0, 0.5, 0.0, 1.0), life=0.6):
        self.pos = [float(pos[0]), float(pos[1]), float(pos[2])]
        self.vel = [float(vel[0]), float(vel[1]), float(vel[2])]
        self.color = color
        self.life = float(life)

    def update(self, dt):
        self.life -= dt
        if self.life <= 0:
            return
        self.pos[0] += self.vel[0] * dt
        self.pos[1] += self.vel[1] * dt
        self.pos[2] += self.vel[2] * dt


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def spawn_hit(self, center, count=12, spread=1.0):
        cx, cy, cz = float(center[0]), float(center[1]), float(center[2])
        for i in range(count):
            ang = random.random() * 2.0 * math.pi
            vel = [math.cos(ang) * random.uniform(0.5, spread), random.uniform(0.5, 1.5), math.sin(ang) * random.uniform(0.5, spread)]
            life = random.uniform(0.4, 0.9)
            col = (1.0, 0.6, 0.2, 1.0)
            p = Particle((cx, cy, cz), vel, color=col, life=life)
            self.particles.append(p)

    def update(self, dt):
        alive = []
        for p in self.particles:
            p.update(dt)
            if p.life > 0:
                alive.append(p)
        self.particles = alive

    def draw(self):
        if not self.particles:
            return
        glPointSize(4.0)
        glBegin(GL_POINTS)
        for p in self.particles:
            alpha = max(0.0, min(1.0, p.life))
            r, g, b, _ = p.color
            glColor4f(r, g, b, alpha)
            glVertex3f(p.pos[0], p.pos[1], p.pos[2])
        glEnd()
