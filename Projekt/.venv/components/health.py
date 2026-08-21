"""Health component."""

class Health:
    def __init__(self, max_hp=10):
        self.max = max_hp
        self.current = max_hp

    def is_dead(self):
        return self.current <= 0

    def apply_damage(self, amount):
        self.current = max(0, self.current - amount)
