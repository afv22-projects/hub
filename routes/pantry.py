from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from models.pantry import (
    Ingredient as IngredientModel,
    Recipe as RecipeModel,
)
from schemas.pantry import (
    IngredientCreate,
    IngredientSchema,
    IngredientUpdate,
    RecipeCreate,
    RecipeSchema,
    RecipeUpdate,
)

router = APIRouter(prefix="/pantry")


@router.get("/recipes", response_model=list[RecipeSchema])
def get_recipes(db: Session = Depends(get_db)):
    return db.query(RecipeModel).all()


@router.get("/recipes/{id}", response_model=RecipeSchema)
def get_recipe(id: int, db: Session = Depends(get_db)):
    db_recipe = db.get(RecipeModel, id)
    if not db_recipe:
        raise HTTPException(404, f"Recipe not found (id: {id})")
    return db_recipe


@router.post("/recipes", response_model=RecipeSchema)
def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
    db_recipe = RecipeModel(name=recipe.name, notes=recipe.notes)
    db.add(db_recipe)

    for ingredient in recipe.ingredients:
        db_ingredient = (
            db.query(IngredientModel).filter_by(name=ingredient).one_or_none()
        )
        if not db_ingredient:
            db_ingredient = IngredientModel(name=ingredient)
            db.add(db_ingredient)
        db_recipe.ingredients.append(db_ingredient)

    try:
        db.commit()
        db.refresh(db_recipe)
        return db_recipe
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Failed to create recipe due to constraint violation",
        )


@router.post("/recipes/{id}/ingredients", response_model=RecipeSchema)
def add_ingredient_to_recipe(id: int, name: str, db: Session = Depends(get_db)):
    db_recipe = db.get(RecipeModel, id)
    if not db_recipe:
        raise HTTPException(404, f"Recipe not found (id: {id})")

    db_ingredient = db.query(IngredientModel).filter_by(name=name).one_or_none()
    if not db_ingredient:
        db_ingredient = IngredientModel(name=name)
        db.add(db_ingredient)

    if db_ingredient not in db_recipe.ingredients:
        db_recipe.ingredients.append(db_ingredient)

    try:
        db.commit()
        db.refresh(db_recipe)
        return db_recipe
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ingredient with name '{name}' already exists",
        )


@router.delete("/recipes/{id}/ingredients", response_model=RecipeSchema)
def remove_ingredient_from_recipe(
    id: int, ingredient: str, db: Session = Depends(get_db)
):
    db_recipe = db.get(RecipeModel, id)
    if not db_recipe:
        raise HTTPException(404, f"Recipe not found (id: {id})")

    db_ingredient = db.query(IngredientModel).filter_by(name=ingredient).one_or_none()
    if not db_ingredient:
        raise HTTPException(404, f"Ingredient '{ingredient}' not found")

    if db_ingredient in db_recipe.ingredients:
        db_recipe.ingredients.remove(db_ingredient)

    db.commit()
    return db_recipe


@router.patch("/recipes/{id}", response_model=RecipeSchema)
def update_recipe(id: int, recipe: RecipeUpdate, db: Session = Depends(get_db)):
    db_recipe = db.get(RecipeModel, id)
    if not db_recipe:
        raise HTTPException(404, f"Recipe not found (id: {id})")

    if recipe.name is not None:
        db_recipe.name = recipe.name
    if recipe.notes is not None:
        db_recipe.notes = recipe.notes

    db.commit()
    return db_recipe


@router.delete("/recipes/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(id: int, db: Session = Depends(get_db)):
    db_recipe = db.get(RecipeModel, id)
    if not db_recipe:
        raise HTTPException(404, f"Recipe not found (id: {id})")

    db.delete(db_recipe)
    db.commit()


@router.get("/ingredients", response_model=list[IngredientSchema])
def get_ingredients(db: Session = Depends(get_db)):
    return db.query(IngredientModel).all()


@router.post("/ingredients", response_model=IngredientSchema)
def create_ingredient(ingredient: IngredientCreate, db: Session = Depends(get_db)):
    db_ingredient = IngredientModel(
        name=ingredient.name,
        needed=ingredient.needed,
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


@router.patch("/ingredients/{id}", response_model=IngredientSchema)
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

    try:
        db.commit()
        return db_ingredient
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ingredient with name '{ingredient.name}' already exists",
        )


@router.delete("/ingredients/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient(id: int, db: Session = Depends(get_db)):
    db_ingredient = db.get(IngredientModel, id)
    if not db_ingredient:
        raise HTTPException(404, f"Ingredient not found (id: {id})")

    db.delete(db_ingredient)
    db.commit()
