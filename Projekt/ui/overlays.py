"""Full-screen menu and game-state overlays."""

from __future__ import annotations


class GameOverlays:
    """Render non-gameplay screens through the shared renderer interface."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    def draw_menu(self, renderer, text, selected_option: int) -> None:
        renderer.begin_hud()
        renderer.draw_hud_quad(0, 0, self.width, self.height, (0.05, 0.05, 0.1))
        renderer.draw_text(text, "3D ZOMBIE LOOTER SHOOTER", self.width // 2, 150, "huge", (200, 50, 50), center=True)
        renderer.draw_text(text, "Survive the endless waves", self.width // 2, 240, "med", (200, 200, 200), center=True)
        for index, label in enumerate(("New Game", "Quit")):
            color = (255, 220, 100) if index == selected_option else (200, 200, 200)
            renderer.draw_text(text, label, self.width // 2, 400 + index * 60, "large", color, center=True)
        renderer.draw_text(text, "WASD: Move | Mouse: Aim | LMB: Shoot | R: Reload | Shift: Sprint | F: Medkit | 1-3: Weapons", self.width // 2, self.height - 50, "small", (180, 180, 180), center=True)
        renderer.draw_text(text, "ESC: Pause | Up/Down: Navigate | Enter: Select", self.width // 2, self.height - 25, "small", (180, 180, 180), center=True)
        renderer.end_hud()

    def draw_pause(self, renderer, text) -> None:
        renderer.begin_hud()
        renderer.draw_hud_quad(0, 0, self.width, self.height, (0, 0, 0), alpha=0.6)
        renderer.draw_text(text, "PAUSED", self.width // 2, 200, "huge", (255, 220, 100), center=True)
        renderer.draw_text(text, "ESC: Resume", self.width // 2, 350, "med", (255, 255, 255), center=True)
        renderer.draw_text(text, "R: Restart", self.width // 2, 400, "med", (255, 255, 255), center=True)
        renderer.draw_text(text, "Close window to Quit", self.width // 2, 450, "med", (255, 255, 255), center=True)
        renderer.end_hud()

    def draw_game_over(self, renderer, text, score: int, wave: int, kills: int) -> None:
        renderer.begin_hud()
        renderer.draw_hud_quad(0, 0, self.width, self.height, (0.2, 0, 0), alpha=0.7)
        renderer.draw_text(text, "GAME OVER", self.width // 2, 180, "huge", (255, 50, 50), center=True)
        renderer.draw_text(text, f"Score: {score}", self.width // 2, 320, "large", (255, 220, 100), center=True)
        renderer.draw_text(text, f"Wave Reached: {wave}", self.width // 2, 380, "large", (255, 220, 100), center=True)
        renderer.draw_text(text, f"Total Kills: {kills}", self.width // 2, 440, "med", (255, 255, 255), center=True)
        renderer.draw_text(text, "R: Restart | ESC: Main Menu", self.width // 2, 530, "med", (255, 255, 255), center=True)
        renderer.end_hud()