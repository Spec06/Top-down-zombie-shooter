# py -m pip install pygame-ce PyOpenGL numpy pytest
# Run: python main.py
"""
3D Top-Down Zombie Looter Shooter
"""
import math
import random

import pygame as pg
try:
    import settings
except ModuleNotFoundError:  # package import: python -m Projekt.main
    from Projekt import settings
from components.health import Health
from entities.player import Player
from entities.projectile import Projectile
from entities.enemy import Enemy
from entities.loot import LootItem
from scripts.spawn_manager import SpawnManager
from systems.camera_system import Camera
from systems.render_system import Render_system
from systems.combat_system import CombatSystem
from ui.hud import HUD
from ui.menu import Menu
from pygame.locals import DOUBLEBUF, OPENGL
from systems.input_system import poll_input

WORLD_HALF = 50.0

WEAPONS = {
    "pistol": {"damage": 15, "cooldown": 0.25, "speed": 35.0, "magazine": 12, "color": (0.9, 0.9, 0.3), "spread": 0.02},
    "shotgun": {"damage": 10, "cooldown": 0.8, "speed": 30.0, "magazine": 6, "color": (0.9, 0.5, 0.1), "spread": 0.22},
    "rifle": {"damage": 25, "cooldown": 0.12, "speed": 50.0, "magazine": 20, "color": (0.3, 0.7, 0.9), "spread": 0.05},
}

def main() -> None:
    pg.init()
    screen = pg.display.set_mode(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT),
        DOUBLEBUF | OPENGL,
    )
    pg.display.set_caption("Gambling")
    Render_system.init_opengl(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)

    spawn_manager = SpawnManager(fallback_center=(0.0, 0.0))
    player = spawn_manager.spawn(Player)
    player.health = Health(max_hp=100)
    camera = Camera(player, distance=18.0, pitch=89.9)
    enemies = []
    render_system = Render_system
    combat_system = CombatSystem(world=enemies)
    projectiles: list[Projectile] = []
    loot: list[LootItem] = []
    hud = HUD()
    menu = Menu(items=["Start", "Beenden"], title="3D Zombie Looter Shooter")
    clock = pg.time.Clock()
    running = True
    mode = "menu"
    wave = 0
    score = 0
    kills = 0
    fire_cooldown = 0.0
    reload_timer = 0.0
    weapon_index = 0
    ammo = {name: data["magazine"] * 4 for name, data in WEAPONS.items()}
    magazine = {name: data["magazine"] for name, data in WEAPONS.items()}
    spawn_timer = 0.0
    wave_timer = 3.0
    obstacle_positions = [(-8.0, -5.0), (9.0, 4.0), (4.0, -10.0), (-12.0, 9.0)]

    def _fire_weapon(weapon_name: str, shooter: Player, targets: list[Projectile]) -> None:
        angle = shooter.aim_angle
        spread = WEAPONS[weapon_name].get("spread", 0.0)
        pellet_count = 6 if weapon_name == "shotgun" else 1
        for _ in range(pellet_count):
            shot_angle = angle + random.uniform(-spread, spread)
            direction = (math.cos(shot_angle), 0.0, math.sin(shot_angle))
            projectile = Projectile(
                (shooter.x, 0.8, shooter.z),
                direction,
                speed=WEAPONS[weapon_name]["speed"],
            )
            projectile.damage = WEAPONS[weapon_name]["damage"]
            targets.append(projectile)

    def start_game() -> None:
        nonlocal enemies, projectiles, loot, wave, score, kills, wave_timer, magazine, ammo
        player.position[:] = (0.0, 0.5, 0.0)
        player.health = Health(max_hp=100)
        enemies = []
        projectiles = []
        loot = []
        ammo = {name: data["magazine"] * 4 for name, data in WEAPONS.items()}
        magazine = {name: data["magazine"] for name, data in WEAPONS.items()}
        wave = 0
        score = 0
        kills = 0
        wave_timer = 3.0

    def spawn_wave() -> None:
        nonlocal wave
        wave += 1
        enemies.extend(
            spawn_manager.spawn_enemies(
                Enemy,
                count=min(4 + wave * 2, 18),
                center=(0.0, 0.0),
                radius=18.0,
                hp=35 + wave * 5,
                zombie_types=["normal"] + (["fast"] if wave >= 2 else []) + (["tank"] if wave >= 3 else []),
            )
        )

    while running:
        dt = clock.tick(settings.FPS) / 1000.0
        input_state = poll_input()
        running = not input_state["quit"]
        if not running:
            break

        if mode == "menu":
            menu_action = menu.handle_input(input_state)
            if menu_action == "start":
                if menu.selected == 0:
                    start_game()
                    mode = "game"
                else:
                    running = False
            if running:
                menu.show(screen)
            continue
        if mode == "game_over":
            if any(event.type == pg.KEYDOWN and event.key == pg.K_r for event in input_state["events"]):
                start_game()
                mode = "game"
            elif any(event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE for event in input_state["events"]):
                mode = "menu"
            pg.display.set_caption(f"GAME OVER | Score {score} | Kills {kills} | R: Neustart | ESC: Menue")
            continue

        if mode == "paused":
            if any(event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE for event in input_state["events"]):
                mode = "game"
            continue
        if any(event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE for event in input_state["events"]):
            mode = "paused"
            continue

        keys = input_state["keys"]
        input_state["mouse_world"] = camera.world_from_screen(
            input_state["mouse"]["pos"], settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
        )
        player.update(dt, input_state)
        fire_cooldown = max(0.0, fire_cooldown - dt)
        reload_timer = max(0.0, reload_timer - dt)

        for event in input_state["events"]:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r and reload_timer <= 0:
                    weapon = list(WEAPONS)[weapon_index]
                    reload_timer = 1.2
                elif event.key in (pg.K_1, pg.K_2, pg.K_3):
                    weapon_index = event.key - pg.K_1
                elif event.key == pg.K_SPACE and fire_cooldown <= 0:
                    weapon = list(WEAPONS)[weapon_index]
                    if magazine[weapon] > 0:
                        magazine[weapon] -= 1
                        fire_cooldown = WEAPONS[weapon]["cooldown"]
                        _fire_weapon(weapon, player, projectiles)
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and fire_cooldown <= 0:
                weapon = list(WEAPONS)[weapon_index]
                if magazine[weapon] > 0:
                    magazine[weapon] -= 1
                    fire_cooldown = WEAPONS[weapon]["cooldown"]
                    _fire_weapon(weapon, player, projectiles)

        if reload_timer == 0 and magazine[list(WEAPONS)[weapon_index]] < WEAPONS[list(WEAPONS)[weapon_index]]["magazine"]:
            weapon = list(WEAPONS)[weapon_index]
            amount = min(WEAPONS[weapon]["magazine"] - magazine[weapon], ammo[weapon])
            magazine[weapon] += amount
            ammo[weapon] -= amount

        for projectile in projectiles:
            projectile.update(dt)
        projectiles = [projectile for projectile in projectiles if projectile.is_alive()]
        camera.update(player)

        spawn_timer += dt
        if not enemies and spawn_timer > wave_timer:
            spawn_timer = 0.0
            spawn_wave()
        for enemy in enemies:
            if not enemy.is_dead():
                enemy.update(dt, player)
                if math.hypot(enemy.x - player.x, enemy.z - player.z) < 1.25 and enemy.can_attack():
                    player.health.take_damage(enemy.stats["damage"])
        before = len(enemies)
        projectiles = combat_system.handle_projectiles(projectiles, enemies)
        defeated = [enemy for enemy in enemies if enemy.is_dead()]
        for enemy in defeated:
            drop_type = random.choice(["medkit", "pistol", "shotgun", "rifle", "stamina"])
            loot.append(LootItem(enemy.x, enemy.z, drop_type, 25 if drop_type in ("medkit", "stamina") else 8))
        enemies = [enemy for enemy in enemies if not enemy.is_dead()]
        kills += before - len(enemies)
        score += (before - len(enemies)) * 10
        remaining_loot = []
        for item in loot:
            if math.hypot(item.x - player.x, item.z - player.z) < 1.15 and item.collect(player, ammo, magazine, WEAPONS):
                continue
            remaining_loot.append(item)
        loot = remaining_loot
        if player.health.is_dead():
            mode = "game_over"

        render_system.begin_frame()
        camera.apply()
        render_system.draw_ground()
        for x, z in obstacle_positions:
            render_system.draw_cube((x, 1.0, z), 2.0, (0.35, 0.28, 0.22))
        render_system.draw_cylinder((player.x, 0.0, player.z), 0.5, 1.3, (0.15, 0.75, 0.25))
        render_system.draw_cylinder((player.x, 1.3, player.z), 0.32, 0.35, (0.85, 0.65, 0.45))
        for projectile in projectiles:
            render_system.draw_cube(projectile.position, 0.16, WEAPONS[list(WEAPONS)[weapon_index]]["color"])
        for item in loot:
            loot_colors = {"medkit": (0.9, 0.15, 0.15), "stamina": (0.1, 0.7, 0.95), "pistol": (0.9, 0.9, 0.25), "shotgun": (0.9, 0.5, 0.1), "rifle": (0.3, 0.7, 0.9)}
            render_system.draw_cube(item.position, 0.35, loot_colors[item.loot_type])
        for enemy in enemies:
            if not enemy.is_dead():
                scale = enemy.stats["scale"]
                render_system.draw_cylinder((enemy.x, 0.0, enemy.z), 0.5 * scale, 1.4 * scale, enemy.stats["color"])
                render_system.draw_cylinder((enemy.x, 1.4 * scale, enemy.z), 0.3 * scale, 0.3 * scale, (0.55, 0.4, 0.2))
        hud.draw(screen, player, list(WEAPONS)[weapon_index], magazine[list(WEAPONS)[weapon_index]], ammo[list(WEAPONS)[weapon_index]], input_state["mouse"]["pos"])
        render_system.end_frame()
        pg.display.set_caption(
            f"Gambling | Wave {wave} | HP {int(player.health.current)}/{int(player.health.max_hp)} | "
            f"Score {score} | Kills {kills} | {list(WEAPONS)[weapon_index].title()} "
            f"{magazine[list(WEAPONS)[weapon_index]]}/{ammo[list(WEAPONS)[weapon_index]]} | "
            "WASD Bewegen | Shift Sprint | Maus/LMB Schiessen | R Nachladen | 1-3 Waffen | ESC Pause"
        )
    pg.quit()

if __name__ == "__main__":
    main()