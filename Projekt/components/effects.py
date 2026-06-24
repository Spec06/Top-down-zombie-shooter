"""Simple visual effect components: FlashEffect."""

class FlashEffect:
    def __init__(self, duration: float = 0.2):
        self.duration = float(duration)
        self.remaining = float(duration)

    def update(self, dt: float):
        self.remaining = max(0.0, self.remaining - float(dt))

    def is_active(self) -> bool:
        return self.remaining > 0.0
