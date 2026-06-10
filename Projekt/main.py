import pygame

from settings import *
from logic.game_manager import GameManager
from ui.button import Button

pygame.init()

screen = pygame.display.set_mode(
(WIDTH, HEIGHT)
)

clock = pygame.time.Clock()

font = pygame.font.SysFont(
"arial",
28
)

game = GameManager()
game.new_round()

check_btn = Button(
50, 630, 150, 50, "Check"
)

call_btn = Button(
230, 630, 150, 50, "Call"
)

raise_btn = Button(
410, 630, 150, 50, "Raise"
)

fold_btn = Button(
590, 630, 150, 50, "Fold"
)

running = True

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if check_btn.is_clicked(event.pos):
                print("Check")

            if call_btn.is_clicked(event.pos):
                print("Call")

            if raise_btn.is_clicked(event.pos):
                print("Raise")

            if fold_btn.is_clicked(event.pos):
                print("Fold")

    screen.fill(GREEN)

    check_btn.draw(screen, font)
    call_btn.draw(screen, font)
    raise_btn.draw(screen, font)
    fold_btn.draw(screen, font)

    pygame.display.flip()

pygame.quit()