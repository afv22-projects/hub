from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from models.pantry import DBIngredient, Recipe as RecipeModel
from schemas.pantry import RecipeCreate, RecipeSchema, RecipeUpdate

router = APIRouter(prefix="/recipes")


@router.post("/{id}/ingredients", response_model=RecipeSchema)
def add_ingredient_to_recipe(id: int, name: str, db: Session = Depends(get_db)):
    db_recipe = db.get(RecipeModel, id)
    if not db_recipe:
        raise HTTPException(404, f"Recipe not found (id: {id})")

    db_ingredient = db.query(DBIngredient).filter_by(name=name).one_or_none()
    if not db_ingredient:
        db_ingredient = DBIngredient(name=name)
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


@router.delete("/{id}/ingredients", response_model=RecipeSchema)
def remove_ingredient_from_recipe(
    id: int, ingredient: str, db: Session = Depends(get_db)
):
    db_recipe = db.get(RecipeModel, id)
    if not db_recipe:
        raise HTTPException(404, f"Recipe not found (id: {id})")

    db_ingredient = db.query(DBIngredient).filter_by(name=ingredient).one_or_none()
    if not db_ingredient:
        raise HTTPException(404, f"Ingredient '{ingredient}' not found")

    if db_ingredient in db_recipe.ingredients:
        db_recipe.ingredients.remove(db_ingredient)

    db.commit()
    return db_recipe


@router.post("/{id}/sources", response_model=RecipeSchema)
def add_source_to_recipe(id: int, source: str, db: Session = Depends(get_db)):
    db_recipe = db.get(RecipeModel, id)
    if not db_recipe:
        raise HTTPException(404, f"Recipe not found (id: {id})")

    db_recipe.sources = db_recipe.sources + [source]
    db.commit()
    return db_recipe


@router.delete("/{id}/sources", response_model=RecipeSchema)
def remove_source_from_recipe(id: int, source: str, db: Session = Depends(get_db)):
    db_recipe = db.get(RecipeModel, id)
    if not db_recipe:
        raise HTTPException(404, f"Recipe not found (id: {id})")

    if source in db_recipe.sources:
        db_recipe.sources = [src for src in db_recipe.sources if src != source]

    db.commit()
    return db_recipe


@router.post("/{id}/tags", response_model=RecipeSchema)
def add_tag_to_recipe(id: int, tag: str, db: Session = Depends(get_db)):
    db_recipe = db.get(RecipeModel, id)
    if not db_recipe:
        raise HTTPException(404, f"Recipe not found (id: {id})")

    db_recipe.tags = db_recipe.tags + [tag]
    db.commit()
    return db_recipe


@router.delete("/{id}/tags", response_model=RecipeSchema)
def remove_tag_from_recipe(id: int, tag: str, db: Session = Depends(get_db)):
    db_recipe = db.get(RecipeModel, id)
    if not db_recipe:
        raise HTTPException(404, f"Recipe not found (id: {id})")

    if tag in db_recipe.tags:
        db_recipe.tags = [db_tag for db_tag in db_recipe.tags if db_tag != tag]

    db.commit()
    return db_recipe


@router.get("/{id}", response_model=RecipeSchema)
def get_recipe(id: int, db: Session = Depends(get_db)):
    db_recipe = db.get(RecipeModel, id)
    if not db_recipe:
        raise HTTPException(404, f"Recipe not found (id: {id})")
    return db_recipe


@router.patch("/{id}", response_model=RecipeSchema)
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


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(id: int, db: Session = Depends(get_db)):
    db_recipe = db.get(RecipeModel, id)
    if not db_recipe:
        raise HTTPException(404, f"Recipe not found (id: {id})")

    db.delete(db_recipe)
    db.commit()


@router.get("", response_model=list[RecipeSchema])
def get_recipes(db: Session = Depends(get_db)):
    return db.query(RecipeModel).all()


@router.post("", response_model=RecipeSchema)
def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
    db_recipe = RecipeModel(
        name=recipe.name,
        notes=recipe.notes,
        sources=recipe.sources,
        tags=recipe.tags,
    )
    db.add(db_recipe)

    for ingredient in recipe.ingredients:
        db_ingredient = (
            db.query(DBIngredient).filter_by(name=ingredient).one_or_none()
        )
        if not db_ingredient:
            db_ingredient = DBIngredient(name=ingredient)
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
