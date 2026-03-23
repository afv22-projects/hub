from pathlib import Path

from mdorm import MDorm

mdorm: MDorm | None = None


def init_db(models_dir: Path, db_url: str) -> None:
    global mdorm

    if not mdorm:
        from .models import Consumable, Ingredient, Recipe

        mdorm = MDorm(models_dir, db_url)


def get_db() -> MDorm:
    global mdorm
    if not mdorm:
        raise RuntimeError("MDorm not initialized")
    return mdorm
