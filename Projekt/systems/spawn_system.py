"""Enemy and wave spawning orchestration."""

from __future__ import annotations

import math
import random

from Projekt import settings
from Projekt.entities.enemy import Enemy
from Projekt.scripts.spawn_manager import SpawnManager


class WaveManager:
	"""Control wave timing and delegate enemy creation to SpawnManager."""

	def __init__(self, enemy_class=Enemy, spawn_manager: SpawnManager | None = None) -> None:
		self.enemy_class = enemy_class
		self.spawn_manager = spawn_manager or SpawnManager()
		self.wave = 0
		self.to_spawn = 0
		self.spawn_timer = 0.0
		self.spawn_interval = 1.0
		self.between_waves = True
		self.countdown = 5.0
		self.kills_this_wave = 0

	def update(self, dt: float, game) -> None:
		if self.between_waves:
			self.countdown -= dt
			if self.countdown <= 0:
				self._start_wave()
			return

		if self.to_spawn > 0:
			self.spawn_timer -= dt
			if self.spawn_timer <= 0:
				self._spawn_enemy(game)
				self.to_spawn -= 1
				self.spawn_timer = self.spawn_interval
			return

		if not game.zombies:
			self.between_waves = True
			self.countdown = 10.0
			game.player.ammo["pistol"] += 10
			game.add_feedback(
				"Wave Cleared! +10 Pistol Ammo",
				game.player.pos[:],
				(0, 1, 0),
			)

	def _start_wave(self) -> None:
		self.wave += 1
		self.kills_this_wave = 0
		self.to_spawn = int(5 * (1.2 ** (self.wave - 1))) + self.wave
		self.between_waves = False
		self.spawn_timer = 0.0
		self.spawn_interval = max(0.2, 1.0 - self.wave * 0.05)

	def _spawn_enemy(self, game) -> None:
		while True:
			angle = random.uniform(0, math.tau)
			distance = random.uniform(22.0, 30.0)
			x = game.player.pos[0] + math.cos(angle) * distance
			z = game.player.pos[2] + math.sin(angle) * distance
			x = max(-settings.WORLD_HALF + 2, min(settings.WORLD_HALF - 2, x))
			z = max(-settings.WORLD_HALF + 2, min(settings.WORLD_HALF - 2, z))
			zombie_type = self._select_enemy_type()
			size = self._enemy_size(zombie_type)
			if not self._blocked(x, z, size, game):
				break

		game.zombies.append(
			self.spawn_manager.spawn_enemy(
				self.enemy_class,
				x,
				z,
				zombie_type,
			)
		)

	def _select_enemy_type(self) -> str:
		roll = random.random()
		if self.wave >= 3 and roll < 0.15:
			return "tank"
		if self.wave >= 2 and roll < 0.40:
			return "fast"
		return "normal"

	@staticmethod
	def _enemy_size(enemy_type: str) -> float:
		return {"normal": 0.3, "fast": 0.2, "tank": 0.5}[enemy_type]

	@staticmethod
	def _blocked(x: float, z: float, half_size: float, game) -> bool:
		for obstacle in game.obstacles:
			if abs(x - obstacle["x"]) < half_size + obstacle["w"] / 2:
				if abs(z - obstacle["z"]) < half_size + obstacle["d"] / 2:
					return True
		for wall in game.walls:
			if abs(x - wall["x"]) < half_size + wall["w"] / 2:
				if abs(z - wall["z"]) < half_size + wall["d"] / 2:
					return True
		return False

__all__ = ["SpawnManager", "WaveManager"]
