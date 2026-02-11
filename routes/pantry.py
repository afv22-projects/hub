from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from models.pantry import Recipe as RecipeModel
from schemas.pantry import RecipeCreate, Recipe as RecipeSchema

router = APIRouter(prefix="/pantry")


@router.get("/recipes", response_model=list[RecipeSchema])
def get_recipes(db: Session = Depends(get_db)):
    return db.query(RecipeModel).all()


@router.post("/recipes")
def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
    db_recipe = RecipeModel(
        name=recipe.name,
        notes=recipe.notes,
    )
    db.add(db_recipe)
    db.commit()


@router.patch("/recipes")
def update_recipe(recipe: RecipeSchema, db: Session = Depends(get_db)):
    db_recipe = db.query(RecipeModel).get(recipe.id)
    if not db_recipe:
        raise KeyError(f"Recipe not found (id: {recipe.id})")
    db_recipe.name = recipe.name
    db_recipe.notes = recipe.notes
    db.commit()


@router.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    db_recipe = db.query(RecipeModel).get(recipe_id)
    db.delete(db_recipe)
    db.commit()
