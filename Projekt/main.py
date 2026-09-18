# py -m pip install pygame-ce PyOpenGL numpy pytest
# Run: main_game.py

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from Projekt.game import Game


def main() -> None:
    Game().run()


if __name__ == "__main__":
    main()
