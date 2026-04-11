import logging
from pathlib import Path

from mdorm import MDorm, LocalFiles

logger = logging.getLogger(__name__)

mdorm: MDorm | None = None


def init_db(models_dir: Path, db_url: str) -> None:
    global mdorm

    if mdorm:
        logger.debug("MDorm already initialized, skipping")
        return

    logger.info(f"Initializing pantry MDorm: models_dir={models_dir}, db_url={db_url}")

    try:
        from .models import Consumable, Ingredient, Recipe
    except ImportError as e:
        logger.error(f"Failed to import models: {e}")
        raise

    try:
        mdorm = MDorm(
            LocalFiles(models_dir),
            db_url,
            logger=logger,
        )
        logger.info("pantry_v2 db initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MDorm: {e}")
        raise


def get_db() -> MDorm:
    global mdorm
    if not mdorm:
        logger.error("get_db called but MDorm not initialized")
        raise RuntimeError("MDorm not initialized")
    return mdorm
