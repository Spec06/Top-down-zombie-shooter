"""Attack component: stores attack parameters and cooldown tracking."""
import time

class Attack:
    def __init__(self, damage, range, cooldown, attack_type, knockback):
        self.damage = damage
        self.range = range
        self.cooldown = cooldown
        self.attack_type = attack_type
        self.knockback = knockback
        self._last_attack_time = -float("inf")

    def can_attack(self):
        return (time.time() - self._last_attack_time) >= self.cooldown

    def trigger(self):
        self._last_attack_time = time.time()
