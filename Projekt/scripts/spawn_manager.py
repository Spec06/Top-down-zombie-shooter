"""Spawn manager scaffold."""

class SpawnManager:
    def __init__(self):
        self.spawn_points = []

    def spawn(self, entity_cls, point):
        return entity_cls(*point)
