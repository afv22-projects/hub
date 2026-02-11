from pydantic import BaseModel, ConfigDict

from enums import IngredientCategory


class IngredientBase(BaseModel):
    name: str
    needed: bool
    category: IngredientCategory


class IngredientCreate(IngredientBase): ...


class IngredientUpdate(BaseModel):
    name: str | None = None
    needed: bool | None = None
    category: IngredientCategory | None = None


class IngredientSchema(IngredientBase):
    id: int
    recipe_ids: list[int]

    model_config = ConfigDict(from_attributes=True)
