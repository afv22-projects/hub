from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from db.pantry import DBIngredient
from enums import IngredientCategory
from schemas.pantry import Ingredient, IngredientCreate, IngredientUpdate

router = APIRouter(prefix="/ingredients")


@router.get("/{id}", response_model=Ingredient)
def get_ingredient(id: str, db: Session = Depends(get_db)):
    db_ingredient = db.get(DBIngredient, id)
    if not db_ingredient:
        raise HTTPException(404, f"Ingredient not found (id: {id})")
    return db_ingredient


@router.patch("/{id}", response_model=Ingredient)
def update_ingredient(
    id: str, ingredient: IngredientUpdate, db: Session = Depends(get_db)
):
    db_ingredient = db.get(DBIngredient, id)
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
def delete_ingredient(id: str, db: Session = Depends(get_db)):
    db_ingredient = db.get(DBIngredient, id)
    if not db_ingredient:
        raise HTTPException(404, f"Ingredient not found (id: {id})")

    db.delete(db_ingredient)
    db.commit()


@router.get("", response_model=list[Ingredient])
def get_ingredients(db: Session = Depends(get_db)):
    return db.query(DBIngredient).all()


@router.post("", response_model=Ingredient)
def create_ingredient(ingredient: IngredientCreate, db: Session = Depends(get_db)):
    db_ingredient = DBIngredient(
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


@router.put("", response_model=Ingredient)
def upsert_ingredient(ingredient: IngredientCreate, db: Session = Depends(get_db)):
    ingredient.name = ingredient.name.lower()
    db_ingredient = (
        db.query(DBIngredient).filter(DBIngredient.name == ingredient.name).first()
    )

    if db_ingredient:
        db_ingredient.needed = ingredient.needed
        if ingredient.category != IngredientCategory.OTHER:
            db_ingredient.category = ingredient.category
    else:
        db_ingredient = DBIngredient(
            name=ingredient.name,
            needed=ingredient.needed,
            category=ingredient.category,
        )
        db.add(db_ingredient)

    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient
