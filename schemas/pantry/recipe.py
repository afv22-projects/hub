from pydantic import BaseModel


class RecipeBase(BaseModel):
    name: str
    notes: str


class RecipeCreate(RecipeBase): ...


class Recipe(RecipeBase):
    id: int
