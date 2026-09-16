"""Active entry point for the full top-down zombie shooter."""

from pathlib import Path
import runpy


REFERENCE_GAME = Path(__file__).resolve().parent.parent / "not needed" / "main_game.py"


def main() -> None:
    """Run the complete reference implementation used by the project."""
    if not REFERENCE_GAME.is_file():
        raise FileNotFoundError(f"Reference game not found: {REFERENCE_GAME}")
    runpy.run_path(str(REFERENCE_GAME), run_name="__main__")


if __name__ == "__main__":
    main()
