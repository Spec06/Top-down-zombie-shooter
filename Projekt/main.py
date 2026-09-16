# py -m pip install pygame-ce PyOpenGL numpy pytest
# Run: python main.py
"""
3D Top-Down Zombie Looter Shooter
"""
import pygame as pg
import settings
from components.health import Health
from entities.player import Player
from entities.projectile import Projectile
from entities.enemy import Enemy
from scripts.spawn_manager import SpawnManager
from systems.camera_system import Camera
from systems.render_system import Render_system
from systems.combat_system import CombatSystem
from ui.hud import HUD
from ui.menu import Menu
from pygame.locals import DOUBLEBUF, OPENGL
from systems.input_system import poll_input

SCREEN_W, SCREEN_H = 1200, 800
FPS = 120
WORLD_HALF = 50.0

def main() -> None:
    pg.init()
    screen = pg.display.set_mode(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), DOUBLEBUF | OPENGL
    )
    Render_system.init_opengl(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    spawn_manager = SpawnManager(fallback_center=(0.0, 0.0))
    player = spawn_manager.spawn(Player)
    player.health = Health(max_hp=100)
    camera = Camera(player)
    enemies = spawn_manager.spawn_enemies(
        Enemy,
        count=5,
        center=(0.0, 0.0),
        radius=12.0,
        hp=10,
    )
    render_system = Render_system
    combat_system = CombatSystem(world=enemies)
    projectiles: list[Projectile] = []
    hud = HUD()
    menu = Menu(items=["Start", "Beenden"], title="Gambling")
    clock = pg.time.Clock()
    running = True
    mode = "menu"
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
                    mode = "game"
                else:
                    running = False
            if running:
                menu.show(screen)
            continue

        player.update(dt, input_state)
        if any(
            event.type == pg.KEYDOWN and event.key == pg.K_SPACE
            for event in input_state["events"]
        ):
            projectiles.append(
                Projectile((player.x, 0.5, player.z), (0.0, 0.0, -1.0))
            )
        for projectile in projectiles:
            projectile.update(dt)
        projectiles = [projectile for projectile in projectiles if projectile.is_alive()]
        camera.update(player)
        render_system.begin_frame()
        camera.apply()
        render_system.draw_ground()
        render_system.draw_cube(
            (player.x, 0.5, player.z),
            1.0,
            (0.2, 0.7, 1.0),
        )
        for projectile in projectiles:
            render_system.draw_cube(projectile.position, 0.2, (1.0, 0.8, 0.1))
        for enemy in enemies:
            if not enemy.is_dead():
                render_system.draw_cube(
                    (enemy.x, 0.5, enemy.z),
                    1.0,
                    (1.2, 1.7, 1.0),
                )
                enemy.update(dt, player)
        render_system.end_frame()
        projectiles = combat_system.handle_projectiles(projectiles, enemies)
        hud.draw(screen, player)
        pg.display.flip()
    pg.quit()

if __name__ == "__main__":
    main()