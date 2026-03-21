from pathlib import Path

from mdorm import MDorm

mdorm: MDorm | None = None


def get_db() -> MDorm:
    global mdorm
    if not mdorm:
        mdorm = MDorm(Path("data/pantry"))
    return mdorm
