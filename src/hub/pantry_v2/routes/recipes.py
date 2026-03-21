from fastapi import APIRouter, Depends

from mdorm import MDorm
from hub.enums.ingredient_category import IngredientCategory
from hub.pantry_v2 import get_db
from hub.pantry_v2.models import Recipe, Ingredient

router = APIRouter(prefix="/recipes")


@router.get("/{name}", response_model=Recipe)
def get_recipe(name: str, db: MDorm = Depends(get_db)):
    return db.get(Recipe, name)


@router.get("", response_model=list[Recipe])
def get_recipes(db: MDorm = Depends(get_db)):
    return db.query(Recipe)


@router.post("", response_model=None)
def create_recipe(recipe: Recipe, db: MDorm = Depends(get_db)):
    db.create(recipe)
    for title in recipe.ingredients:
        ingredient = Ingredient(
            title=title,
            category=IngredientCategory.OTHER,
        )
        db.upsert(ingredient)
