"""HUD scaffold."""

class HUD:
    def __init__(self):
        pass

    def draw(self, screen, entity):
        health_text = f"Health: {entity.health}"
        stamina_text = f"Stamina: {entity.stamina}"
        return
