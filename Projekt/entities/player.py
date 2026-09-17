
import math
import random

import numpy as np
import pygame as pg

from Projekt.components.health import Health
from Projekt.components.weapon import WEAPON_CONFIG
from Projekt.entities.projectile import Projectile
from Projekt.systems.render_system import mat4_mul, mat4_rotate_y, mat4_scale, mat4_translate

try:
    from Projekt import settings
except ModuleNotFoundError:  # pragma: no cover - legacy local layout
    import settings
try:
    from Projekt.entities.entity import Entity
except ModuleNotFoundError:  # pragma: no cover - legacy local layout
    from entities.entity import Entity


class Player(Entity):
    MAX_HP = 100
    MAX_STAMINA = 100

    def __init__(self, x: float = 0.0, z: float = 0.0, radius: float = 0.5) -> None:
        super().__init__(position=(float(x), 0.5, float(z)), radius=radius)
        self.health = Health(self.MAX_HP)
        self.stamina = float(self.MAX_STAMINA)
        self.max_stamina = float(self.MAX_STAMINA)
        self.aim_angle = 0.0
        self.weapons = ["pistol", None, None]
        self.current_weapon = 0
        self.ammo = {"pistol": 48, "shotgun": 0, "rifle": 0}
        self.magazine = {name: data["magazine"] for name, data in WEAPON_CONFIG.items()}
        self.consumables = 1
        self.fire_cooldown = 0.0
        self.reloading = False
        self.reload_timer = 0.0
        self.hit_flash = 0.0
        self.muzzle_flash = 0.0
        self.hurt_cooldown = 0.0

    @property
    def pos(self):
        return self.position

    @property
    def hp(self):
        return self.health.current

    @property
    def current_weapon_key(self):
        return self.weapons[self.current_weapon]

    def switch_weapon(self, index: int) -> None:
        if 0 <= index < len(self.weapons) and self.weapons[index] is not None:
            self.current_weapon = index
            self.reloading = False
            self.fire_cooldown = 0.0

    def try_shoot(self, game) -> None:
        if self.reloading or self.fire_cooldown > 0:
            return
        weapon_key = self.current_weapon_key
        if weapon_key is None:
            return
        weapon = WEAPON_CONFIG[weapon_key]
        if self.magazine[weapon_key] <= 0:
            game.play_sound("empty")
            self.reload(game)
            return
        self.magazine[weapon_key] -= 1
        self.fire_cooldown = weapon["fire_rate"]
        self.muzzle_flash = 0.05
        for _ in range(weapon["pellets"]):
            spread = random.uniform(-weapon["spread"], weapon["spread"])
            angle = self.aim_angle + spread
            direction = np.array([math.cos(angle), 0, math.sin(angle)], dtype=np.float32)
            spawn_position = self.pos + direction * 0.8
            spawn_position[1] = 0.9
            game.bullets.append(Projectile(spawn_position, direction, speed=weapon["bullet_speed"], lifetime=2.0, damage=weapon["damage"], color=weapon["color"]))
        game.play_sound("shoot_" + weapon_key)

    def reload(self, game) -> None:
        weapon_key = self.current_weapon_key
        if self.reloading or weapon_key is None:
            return
        weapon = WEAPON_CONFIG[weapon_key]
        if self.magazine[weapon_key] >= weapon["magazine"] or self.ammo[weapon_key] <= 0:
            return
        self.reloading = True
        self.reload_timer = 0.0
        game.play_sound("reload")

    def _complete_reload(self) -> None:
        weapon_key = self.current_weapon_key
        weapon = WEAPON_CONFIG[weapon_key]
        needed = weapon["magazine"] - self.magazine[weapon_key]
        taken = min(needed, self.ammo[weapon_key])
        self.magazine[weapon_key] += taken
        self.ammo[weapon_key] -= taken
        self.reloading = False

    def take_damage(self, amount: float, game) -> None:
        if self.hurt_cooldown > 0:
            return
        self.health.take_damage(amount)
        self.hit_flash = 0.2
        self.hurt_cooldown = 0.5
        game.shake(0.3, 0.4)
        game.play_sound("hurt")

    def use_medkit(self, game) -> None:
        if self.consumables > 0 and self.hp < self.MAX_HP:
            self.consumables -= 1
            self.health.heal(50)
            game.add_feedback("+50 HP", self.pos[:], (0, 1, 0))
            game.play_sound("pickup")

    def pickup_loot(self, loot, game) -> bool:
        ammo_amounts = {"ammo_pistol": 20, "ammo_shotgun": 6, "ammo_rifle": 20}
        if loot.type in ammo_amounts:
            self.ammo[loot.type.removeprefix("ammo_")] += ammo_amounts[loot.type]
        elif loot.type == "medkit":
            if self.consumables >= 5:
                return False
            self.consumables += 1
        elif loot.type == "weapon_shotgun":
            if self.weapons[1] is None:
                self.weapons[1] = "shotgun"
            else:
                self.ammo["shotgun"] += 6
        elif loot.type == "weapon_rifle":
            if self.weapons[2] is None:
                self.weapons[2] = "rifle"
            else:
                self.ammo["rifle"] += 20
        else:
            return False
        game.play_sound("pickup")
        return True

    @property
    def x(self) -> float:
        return float(self.position[0])

    @x.setter
    def x(self, value):
        self.position[0] = float(value)

    @property
    def z(self) -> float:
        return float(self.position[2])

    @z.setter
    def z(self, value):
        self.position[2] = float(value)

    def update(self, dt: float, game, keys=None) -> None:
        if keys is None:
            keys = pg.key.get_pressed()

        def pressed(key: int) -> bool:
            return bool(keys.get(key, False)) if hasattr(keys, "get") else bool(keys[key])

        move_x = float(pressed(pg.K_d) or pressed(pg.K_RIGHT)) - float(
            pressed(pg.K_a) or pressed(pg.K_LEFT)
        )
        move_z = float(pressed(pg.K_s) or pressed(pg.K_DOWN)) - float(
            pressed(pg.K_w) or pressed(pg.K_UP)
        )

        length = math.hypot(move_x, move_z)
        sprinting = pressed(pg.K_LSHIFT) and length > 0.0 and self.stamina > 0.0
        speed = settings.PLAYER_SPEED * (1.8 if sprinting else 1.0)
        if sprinting:
            self.stamina = max(0.0, self.stamina - 32.0 * dt)
        else:
            self.stamina = min(self.max_stamina, self.stamina + 20.0 * dt)
        new_x = self.x + move_x / max(1.0, length) * speed * dt
        new_z = self.z + move_z / max(1.0, length) * speed * dt
        if not game.is_position_blocked(new_x, self.z, 0.4):
            self.x = max(-settings.WORLD_HALF + 1, min(settings.WORLD_HALF - 1, new_x))
        if not game.is_position_blocked(self.x, new_z, 0.4):
            self.z = max(-settings.WORLD_HALF + 1, min(settings.WORLD_HALF - 1, new_z))

        mouse_world = game.mouse_world
        self.aim_angle = math.atan2(mouse_world[2] - self.z, mouse_world[0] - self.x)
        if pg.mouse.get_pressed()[0] and self.current_weapon_key and WEAPON_CONFIG[self.current_weapon_key]["auto"]:
            self.try_shoot(game)
        if self.reloading:
            self.reload_timer += dt
            if self.reload_timer >= WEAPON_CONFIG[self.current_weapon_key]["reload_time"]:
                self._complete_reload()
        self.fire_cooldown = max(0.0, self.fire_cooldown - dt)
        self.hit_flash = max(0.0, self.hit_flash - dt)
        self.muzzle_flash = max(0.0, self.muzzle_flash - dt)
        self.hurt_cooldown = max(0.0, self.hurt_cooldown - dt)

    def draw(self, renderer) -> None:
        model = mat4_mul(mat4_translate(self.x, 0, self.z), mat4_scale(0.5, 1.4, 0.5))
        flash = self.hit_flash / 0.2 if self.hit_flash > 0 else 0
        renderer.draw_cylinder(model, (0.2, 0.8, 0.2), emissive=(flash, 0, 0))
        renderer.draw_cylinder(mat4_mul(mat4_translate(self.x, 1.4, self.z), mat4_scale(0.35, 0.4, 0.35)), (0.9, 0.7, 0.5), emissive=(flash, 0, 0))