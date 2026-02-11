from pydantic import BaseModel, ConfigDict


class RecipeBase(BaseModel):
    name: str
    notes: str


class RecipeCreate(RecipeBase):
    ingredients: list[str]


class RecipeUpdate(BaseModel):
    name: str | None
    notes: str | None


class RecipeSchema(RecipeBase):
    id: int
    ingredient_ids: list[int] = []

    model_config = ConfigDict(from_attributes=True)
