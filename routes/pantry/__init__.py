from fastapi import APIRouter

from .ingredients import router as ingredients_router
from .recipes import router as recipes_router

router = APIRouter(prefix="/pantry")

router.include_router(recipes_router)
router.include_router(ingredients_router)
