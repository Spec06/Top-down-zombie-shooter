"""NPC entity scaffold."""

class NPC:
    def __init__(self, x=0, y=0):
        self.position = (x, y)
        self.components = {}

    def add_component(self, name, comp):
        self.components[name] = comp

    def get(self, name):
        return self.components.get(name)
