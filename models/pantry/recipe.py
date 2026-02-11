from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, Integer, JSON

from models import Base
from models.pantry.recipe_ingredient_assoc import recipe_ingredient_assoc

if TYPE_CHECKING:
    from models.pantry import Ingredient


class Recipe(Base):
    __tablename__ = "pantry--recipe"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    notes: Mapped[str] = mapped_column(String)
    sources: Mapped[list[str]] = mapped_column(JSON, default=[])

    ingredients: Mapped[list["Ingredient"]] = relationship(
        secondary=recipe_ingredient_assoc, back_populates="recipes"
    )

    @property
    def ingredient_ids(self) -> list[int]:
        return [ingredient.id for ingredient in self.ingredients]

    def __repr__(self) -> str:
        return f"{self.name} (id: {self.id})"
