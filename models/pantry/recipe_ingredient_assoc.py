from sqlalchemy import Column, ForeignKey, Table

from models import Base

recipe_ingredient_assoc = Table(
    "pantry--recipe_ingredient_assoc",
    Base.metadata,
    Column("recipe_id", ForeignKey("pantry--recipe.id")),
    Column("ingredient_id", ForeignKey("pantry--ingredient.id")),
)
