from fastapi import APIRouter

from hub.pantry.enums import (
    CATEGORY_SORT_ORDER,
    ConsumableCategory,
    IngredientCategory,
)

router = APIRouter(prefix="/groceries")


@router.get("/aisles")
def get_aisles() -> dict[IngredientCategory | ConsumableCategory, int]:
    return CATEGORY_SORT_ORDER
