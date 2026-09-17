
from __future__ import annotations

import math
import random

import numpy as np

from Projekt.systems.render_system import mat4_mul, mat4_scale, mat4_translate


class Particle:
	"""Short-lived visual effect with simple gravity and damping."""

	def __init__(self, position, color, speed: float = 3.0) -> None:
		self.pos = np.array(position, dtype=np.float32)
		angle = random.uniform(0, 2 * math.pi)
		elevation = random.uniform(0.5, 2.0)
		self.vel = np.array(
			[math.cos(angle) * speed, elevation * speed, math.sin(angle) * speed],
			dtype=np.float32,
		)
		self.color = color
		self.life = 0.5
		self.max_life = 0.5
		self.size = random.uniform(0.05, 0.15)
		self.dead = False

	def update(self, dt: float) -> None:
		self.pos += self.vel * dt
		self.vel[1] -= 9.8 * dt
		if self.pos[1] < 0:
			self.pos[1] = 0
			self.vel[1] = 0
			self.vel[0] *= 0.5
			self.vel[2] *= 0.5
		self.life -= dt
		if self.life <= 0:
			self.dead = True

	def draw(self, renderer) -> None:
		alpha = max(0, self.life / self.max_life)
		model = mat4_mul(
			mat4_translate(self.pos[0], self.pos[1], self.pos[2]),
			mat4_scale(self.size, self.size, self.size),
		)
		renderer.draw_cube(model, self.color, emissive=self.color, alpha=alpha)
