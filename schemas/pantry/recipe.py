from pydantic import BaseModel, ConfigDict


class RecipeBase(BaseModel):
    name: str
    notes: str
    sources: list[str]


class RecipeCreate(RecipeBase):
    ingredients: list[str]


class RecipeUpdate(BaseModel):
    name: str | None = None
    notes: str | None = None
    sources: list[str] | None = None


class RecipeSchema(RecipeBase):
    id: int
    ingredient_ids: list[int] = []

    model_config = ConfigDict(from_attributes=True)
