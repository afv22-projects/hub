from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from enums import IngredientCategory
from models.pantry import Ingredient as IngredientModel
from schemas.pantry import IngredientCreate, IngredientSchema, IngredientUpdate

router = APIRouter(prefix="/ingredients")


@router.get("/categories", response_model=list[str])
def get_categories():
    return [category.value for category in IngredientCategory]


@router.get("/{id}", response_model=IngredientSchema)
def get_ingredient(id: int, db: Session = Depends(get_db)):
    db_ingredient = db.get(IngredientModel, id)
    if not db_ingredient:
        raise HTTPException(404, f"Ingredient not found (id: {id})")
    return db_ingredient


@router.patch("/{id}", response_model=IngredientSchema)
def update_ingredient(
    id: int, ingredient: IngredientUpdate, db: Session = Depends(get_db)
):
    db_ingredient = db.get(IngredientModel, id)
    if not db_ingredient:
        raise HTTPException(404, f"Ingredient not found (id: {id})")

    if ingredient.name is not None:
        db_ingredient.name = ingredient.name
    if ingredient.needed is not None:
        db_ingredient.needed = ingredient.needed
    if ingredient.category is not None:
        db_ingredient.category = ingredient.category

    try:
        db.commit()
        return db_ingredient
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ingredient with name '{ingredient.name}' already exists",
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient(id: int, db: Session = Depends(get_db)):
    db_ingredient = db.get(IngredientModel, id)
    if not db_ingredient:
        raise HTTPException(404, f"Ingredient not found (id: {id})")

    db.delete(db_ingredient)
    db.commit()


@router.get("/", response_model=list[IngredientSchema])
def get_ingredients(db: Session = Depends(get_db)):
    return db.query(IngredientModel).all()


@router.post("/", response_model=IngredientSchema)
def create_ingredient(ingredient: IngredientCreate, db: Session = Depends(get_db)):
    db_ingredient = IngredientModel(
        name=ingredient.name,
        needed=ingredient.needed,
        category=ingredient.category,
    )
    db.add(db_ingredient)

    try:
        db.commit()
        db.refresh(db_ingredient)
        return db_ingredient
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ingredient with name '{ingredient.name}' already exists",
        )
