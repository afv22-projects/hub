from pydantic import BaseModel, ConfigDict


class IngredientBase(BaseModel):
    name: str


class IngredientCreate(IngredientBase): ...


class IngredientUpdate(BaseModel):
    name: str | None


class IngredientSchema(IngredientBase):
    id: int
    recipe_ids: list[int]

    model_config = ConfigDict(from_attributes=True)
