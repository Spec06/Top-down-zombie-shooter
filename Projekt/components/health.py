

class Health:
    def __init__(self, max_hp: int) -> None:
        self.max_hp = float(max_hp)
        self.current = self.max_hp

    def take_damage(self, amount: float) -> None:
        self.current = max(0.0, self.current - amount)

    def apply_damage(self, amount: float) -> None:
        """Backward-compatible name used by the combat system."""
        self.take_damage(amount)

    def heal(self, amount: float) -> None:
        self.current = min(self.max_hp, self.current + amount)

    def is_dead(self) -> bool:
        return self.current <= 0.0