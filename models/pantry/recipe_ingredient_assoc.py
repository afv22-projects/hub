from sqlalchemy import Column, ForeignKey, Table, UniqueConstraint

from models import Base

recipe_ingredient_assoc = Table(
    "pantry--recipe_ingredient_assoc",
    Base.metadata,
    Column("recipe_id", ForeignKey("pantry--recipe.id")),
    Column("ingredient_id", ForeignKey("pantry--ingredient.id")),
    UniqueConstraint("recipe_id", "ingredient_id", name="uq_recipe_ingredient"),
)
