"""Spawn manager tests."""

from Projekt.scripts.spawn_manager import SpawnManager


class DummyEnemy:
    def __init__(self, x: float, z: float) -> None:
        self.x = x
        self.z = z
        self.components = {}

    def add_component(self, name, component) -> None:
        self.components[name] = component


def test_spawn_manager_spawns_enemies() -> None:
    manager = SpawnManager(fallback_center=(0.0, 0.0))
    enemies = manager.spawn_enemies(DummyEnemy, count=3, center=(0.0, 0.0), radius=4.0)
    assert len(enemies) == 3
    for enemy in enemies:
        assert hasattr(enemy, 'x')
        assert hasattr(enemy, 'z')
