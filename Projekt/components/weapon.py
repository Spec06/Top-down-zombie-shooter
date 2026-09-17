
WEAPON_CONFIG = {
    "pistol": dict(name="Pistol", damage=15, fire_rate=0.25, magazine=12, reload_time=1.2, spread=0.02, bullet_speed=40, pellets=1, color=(0.9, 0.9, 0.3), auto=False),
    "shotgun": dict(name="Shotgun", damage=20, fire_rate=0.8, magazine=6, reload_time=2.0, spread=0.15, bullet_speed=35, pellets=6, color=(0.9, 0.6, 0.2), auto=False),
    "rifle": dict(name="Rifle", damage=30, fire_rate=0.12, magazine=20, reload_time=1.8, spread=0.005, bullet_speed=60, pellets=1, color=(0.3, 0.7, 0.9), auto=True),
}

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