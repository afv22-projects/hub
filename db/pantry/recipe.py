from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, Integer, JSON

from db import DBBase
from .recipe_ingredient_assoc import recipe_ingredient_assoc

if TYPE_CHECKING:
    from .ingredient import DBIngredient


class DBRecipe(DBBase):
    __tablename__ = "pantry--recipe"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    notes: Mapped[str] = mapped_column(String)
    sources: Mapped[list[str]] = mapped_column(JSON, default=[])
    tags: Mapped[list[str]] = mapped_column(JSON, default=[])

    ingredients: Mapped[list["DBIngredient"]] = relationship(
        secondary=recipe_ingredient_assoc, back_populates="recipes"
    )

    @property
    def ingredient_ids(self) -> list[int]:
        return [ingredient.id for ingredient in self.ingredients]

    def __repr__(self) -> str:
        return f"{self.name} (id: {self.id})"
