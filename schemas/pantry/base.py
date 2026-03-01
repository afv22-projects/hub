from pydantic import BaseModel, ConfigDict

from enums import IngredientCategory


class RecipeBase(BaseModel):
    name: str
    notes: str
    sources: list[str]
    tags: list[str]


class RecipeSummary(RecipeBase):
    """Recipe without nested ingredients to avoid circular references."""

    id: str

    model_config = ConfigDict(from_attributes=True)


class IngredientBase(BaseModel):
    name: str
    needed: bool
    category: IngredientCategory


class IngredientSummary(IngredientBase):
    """Ingredient without nested recipes to avoid circular references."""

    id: str

    model_config = ConfigDict(from_attributes=True)
