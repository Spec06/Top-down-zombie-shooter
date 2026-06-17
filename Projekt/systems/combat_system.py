"""Combat system: applies attacks to targets using components."""
import math


class CombatSystem:
    def __init__(self, world=None):
        self.world = world

    @staticmethod
    def _distance(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return math.hypot(dx, dy)

    def perform_melee(self, attacker, attack_comp):
        if not attack_comp.can_attack():
            return []
        attack_comp.record_attack()
        hits = []
        if not hasattr(attacker, 'position'):
            return hits
        atk_pos = attacker.position
        for target in (self.world or []):
            if target is attacker:
                continue
            if not target.get('health'):
                continue
            if not hasattr(target, 'position'):
                continue
            if self._distance(atk_pos, target.position) <= attack_comp.range:
                target.get('health').apply_damage(attack_comp.damage)
                hits.append(target)
        return hits
