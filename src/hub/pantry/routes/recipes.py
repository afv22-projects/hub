from fastapi import APIRouter, Depends, HTTPException, status

from mdorm import MDorm, Response
from hub.pantry import get_db
from hub.pantry.enums import IngredientCategory
from hub.pantry.models import Recipe, Ingredient

router = APIRouter(prefix="/recipes")


@router.post("/{name}/ingredients", status_code=status.HTTP_200_OK)
def add_ingredient_to_recipe(name: str, ing_name: str, db: MDorm = Depends(get_db)):
    try:
        recipe = db.get(Recipe, name)
    except FileNotFoundError:
        raise HTTPException(404, f"Recipe not found (name: {name})")

    ingredient = db.get_or_none(Ingredient, ing_name)
    if not ingredient:
        ingredient = Ingredient(title=ing_name)
        db.create(ingredient)

    if ing_name not in recipe.ingredients:
        recipe.ingredients.append(ing_name)
        db.update(recipe)


@router.delete("/{name}/ingredients", status_code=status.HTTP_204_NO_CONTENT)
def remove_ingredient_from_recipe(
    name: str, ing_name: str, db: MDorm = Depends(get_db)
):
    recipe = db.get_or_none(Recipe, name)
    if not recipe:
        raise HTTPException(404, f"Recipe not found (name: {name})")

    ingredient = db.get_or_none(Ingredient, ing_name)
    if not ingredient:
        raise HTTPException(404, f"Ingredient not found (name: {ing_name})")

    if ing_name in recipe.ingredients:
        recipe.ingredients.remove(ing_name)
        db.update(recipe)


@router.post("/{name}/sources", status_code=status.HTTP_200_OK)
def add_source_to_recipe(name: str, source: str, db: MDorm = Depends(get_db)):
    recipe = db.get_or_none(Recipe, name)
    if not recipe:
        raise HTTPException(404, f"Recipe not found (name: {name})")

    if source and source not in recipe.sources:
        recipe.sources.append(source)
        db.update(recipe)


@router.delete("/{name}/sources", status_code=status.HTTP_204_NO_CONTENT)
def remove_source_from_recipe(name: str, source: str, db: MDorm = Depends(get_db)):
    recipe = db.get_or_none(Recipe, name)
    if not recipe:
        raise HTTPException(404, f"Recipe not found (name: {name})")

    if source in recipe.sources:
        recipe.sources.remove(source)
        db.update(recipe)


@router.post("/{name}/labels", status_code=status.HTTP_200_OK)
def add_label_to_recipe(name: str, label: str, db: MDorm = Depends(get_db)):
    recipe = db.get_or_none(Recipe, name)
    if not recipe:
        raise HTTPException(404, f"Recipe not found (name: {name})")

    if label and label not in recipe.labels:
        recipe.labels.append(label)
        db.update(recipe)


@router.delete("/{name}/labels", status_code=status.HTTP_204_NO_CONTENT)
def remove_label_from_recipe(name: str, label: str, db: MDorm = Depends(get_db)):
    recipe = db.get_or_none(Recipe, name)
    if not recipe:
        raise HTTPException(404, f"Recipe not found (name: {name})")

    if label in recipe.labels:
        recipe.labels.remove(label)
        db.update(recipe)


@router.get("/{name}", response_model=Response[Recipe])
def get_recipe(name: str, db: MDorm = Depends(get_db)):
    recipe = db.get_or_none(Recipe, name)
    if not recipe:
        raise HTTPException(404, f"Recipe not found (name: {name})")
    return recipe


@router.put("/{name}", status_code=status.HTTP_200_OK)
def update_recipe(name: str, recipe: Recipe, db: MDorm = Depends(get_db)):
    try:
        db.update(recipe)
    except FileNotFoundError:
        raise HTTPException(404, f"Recipe not found (name: {name})")


@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(name: str, db: MDorm = Depends(get_db)):
    try:
        db.delete(Recipe, name)
    except FileNotFoundError:
        raise HTTPException(404, f"Recipe not found (name: {name})")


@router.get("", response_model=list[Response[Recipe]])
def get_recipes(db: MDorm = Depends(get_db)):
    return db.query(Recipe)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_recipe(recipe: Recipe, db: MDorm = Depends(get_db)):
    try:
        db.create(recipe)
    except FileExistsError:
        raise HTTPException(409, f"Recipe already exists (name: {recipe.title})")

    for title in recipe.ingredients:
        if not db.files.exists(Ingredient, title):
            ingredient = Ingredient(
                title=title,
                category=IngredientCategory.OTHER,
            )
            db.create(ingredient)
