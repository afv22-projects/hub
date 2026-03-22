from fastapi import APIRouter, Depends, HTTPException, status

from mdorm import MDorm
from hub.pantry_v2 import get_db
from hub.pantry_v2.models import Ingredient

router = APIRouter(prefix="/ingredients")


@router.get("/{name}", response_model=Ingredient)
def get_ingredient(name: str, db: MDorm = Depends(get_db)):
    ingredient = db.get_or_none(Ingredient, name)
    if not ingredient:
        raise HTTPException(404, f"Ingredient not found (name: {name})")
    return ingredient


@router.put("/{name}", status_code=status.HTTP_200_OK)
def update_ingredient(name: str, ingredient: Ingredient, db: MDorm = Depends(get_db)):
    try:
        db.update(ingredient)
    except FileNotFoundError:
        raise HTTPException(404, f"Ingredient not found (name: {name})")


@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient(name: str, db: MDorm = Depends(get_db)):
    try:
        db.delete(Ingredient, name)
    except FileNotFoundError:
        raise HTTPException(404, f"Ingredient not found (name: {name})")


@router.get("", response_model=list[Ingredient])
def get_ingredients(db: MDorm = Depends(get_db)):
    return db.query(Ingredient)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_ingredient(ingredient: Ingredient, db: MDorm = Depends(get_db)):
    try:
        db.create(ingredient)
    except FileExistsError:
        raise HTTPException(
            409, f"Ingredient already exists (name: {ingredient.title})"
        )
