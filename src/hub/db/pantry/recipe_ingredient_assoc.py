from sqlalchemy import Column, ForeignKey, String, Table, UniqueConstraint

from hub.db import DBBase

recipe_ingredient_assoc = Table(
    "pantry--recipe_ingredient_assoc",
    DBBase.metadata,
    Column("recipe_id", String, ForeignKey("pantry--recipe.id")),
    Column("ingredient_id", String, ForeignKey("pantry--ingredient.id")),
    UniqueConstraint("recipe_id", "ingredient_id", name="uq_recipe_ingredient"),
)