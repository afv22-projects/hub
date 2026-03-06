from pydantic import BaseModel, ConfigDict

from enums import IngredientCategory
from .base import IngredientBase, RecipeSummary


class IngredientCreate(IngredientBase): ...


class IngredientUpdate(BaseModel):
    name: str | None = None
    needed: bool | None = None
    category: IngredientCategory | None = None


class Ingredient(IngredientBase):
    id: str
    recipes: list[RecipeSummary]

    model_config = ConfigDict(from_attributes=True)
