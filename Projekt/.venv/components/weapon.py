"""Weapon component (optional): links to attack and weapon-specific data."""

class Weapon:
    def __init__(self, name="Fist", attack=None, ammo=None, fireratio=None):
        self.name = name
        self.attack = attack
        self.ammo = ammo
        self.fireratio = fireratio

    def use(self):
        if self.ammo is not None:
            if self.ammo <= 0:
                return False
            self.ammo -= 1
        return True