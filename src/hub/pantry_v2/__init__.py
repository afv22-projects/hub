from pathlib import Path

from mdorm import MDorm

mdorm: MDorm | None = None


def init_db() -> None:
    global mdorm
    if not mdorm:
        from .models import Consumable, Ingredient, Recipe

        mdorm = MDorm(
            models_dir=Path("data/pantry"),
            db_url="sqlite:///data/appv2.db",
        )


def get_db() -> MDorm:
    global mdorm
    if not mdorm:
        raise RuntimeError("MDorm not initialized")
    return mdorm
