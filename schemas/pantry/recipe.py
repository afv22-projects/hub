from pydantic import BaseModel, ConfigDict


class RecipeBase(BaseModel):
    name: str
    notes: str


class RecipeCreate(RecipeBase): ...


class RecipeUpdate(BaseModel):
    name: str | None
    notes: str | None


class RecipeSchema(RecipeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
