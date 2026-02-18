from pydantic import BaseModel, ConfigDict

from .base import RecipeBase, IngredientSummary


class RecipeCreate(RecipeBase):
    ingredients: list[str]


class RecipeUpdate(BaseModel):
    name: str | None = None
    notes: str | None = None
    sources: list[str] | None = None
    tags: list[str] | None = None


class RecipeSchema(RecipeBase):
    id: int
    ingredients: list[IngredientSummary] = []

    model_config = ConfigDict(from_attributes=True)
