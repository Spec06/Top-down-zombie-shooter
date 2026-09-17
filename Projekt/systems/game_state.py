"""Small systems for transient game state shared by the main loop."""

from __future__ import annotations

import random

import numpy as np


class FeedbackSystem:
    """Manage floating combat and pickup messages."""

    def __init__(self) -> None:
        self.items: list[dict] = []

    def add(self, text, position, color, velocity: float = 1.5) -> None:
        self.items.append(
            {
                "text": text,
                "pos": np.array(position, dtype=np.float32),
                "life": 1.2,
                "max_life": 1.2,
                "vy": velocity,
                "color_rgb": tuple(int(channel * 255) for channel in color),
            }
        )

    def update(self, dt: float) -> None:
        for item in self.items[:]:
            item["life"] -= dt
            item["pos"][1] += item["vy"] * dt
            if item["life"] <= 0:
                self.items.remove(item)

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)


class ScreenShake:
    """Generate a short camera offset after impacts."""

    def __init__(self) -> None:
        self.remaining = 0.0
        self.intensity = 0.0
        self.offset = (0.0, 0.0)

    def trigger(self, duration: float, intensity: float) -> None:
        self.remaining = duration
        self.intensity = intensity

    def update(self, dt: float) -> tuple[float, float]:
        if self.remaining > 0:
            self.remaining -= dt
            strength = max(0.0, self.remaining / 0.3) * self.intensity
            self.offset = (random.uniform(-1, 1) * strength, random.uniform(-1, 1) * strength)
        else:
            self.offset = (0.0, 0.0)
        return self.offset