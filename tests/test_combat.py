import time
import pytest

from Projekt.components.attack import Attack
from Projekt.components.health import Health
from Projekt.entities.enemy import Enemy
from Projekt.systems.combat_system import CombatSystem


def test_attack_cooldown():
    a = Attack(damage=1, range=1.0, cooldown=0.2)
    assert a.can_attack()
    a.record_attack()
    assert not a.can_attack()
    time.sleep(0.25)
    assert a.can_attack()


def test_health_apply_damage():
    h = Health(max_hp=5)
    assert not h.is_dead()
    h.apply_damage(3)
    assert h.current == 2
    h.apply_damage(5)
    assert h.current == 0
    assert h.is_dead()


def test_combat_melee_hits():
    # attacker at origin, enemy at (1.0, 0.5, 0.0)
    class Att:
        def __init__(self):
            self.position = [0.0, 0.5, 0.0]

    attacker = Att()
    enemy = Enemy(1.0, 0.0)
    enemy.add_component('health', Health(max_hp=4))
    world = [enemy]
    combat = CombatSystem(world=world)

    atk = Attack(damage=2, range=2.0, cooldown=0.0)
    hits = combat.perform_melee(attacker, atk)
    assert enemy in hits
    assert enemy.get('health').current == 2
