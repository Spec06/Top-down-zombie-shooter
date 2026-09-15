"""Projectile behavior tests."""

import pytest

from Projekt.entities.projectile import Projectile


def test_projectile_moves() -> None:
    projectile = Projectile([0.0, 0.0, 0.0], [1.0, 0.0, 0.0], speed=10.0, lifetime=1.0)
    projectile.update(0.1)
    assert projectile.position[0] > 0.0
    assert projectile.position[0] == pytest.approx(1.0, abs=0.2)


def test_projectile_expires() -> None:
    projectile = Projectile([0.0, 0.0, 0.0], [1.0, 0.0, 0.0], speed=10.0, lifetime=0.1)
    projectile.update(0.2)
    assert not projectile.is_alive()
