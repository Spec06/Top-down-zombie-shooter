"""Basic health tests."""

from Projekt.components.health import Health


def test_health_takes_damage() -> None:
    health = Health(5)
    health.take_damage(2)
    assert health.current == 3


def test_health_can_die() -> None:
    health = Health(3)
    health.take_damage(4)
    assert health.is_dead()
    assert health.current == 0
