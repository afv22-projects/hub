from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, Integer

from models import Base
from models.pantry.recipe_ingredient_assoc import recipe_ingredient_assoc

if TYPE_CHECKING:
    from models.pantry import Recipe


class Ingredient(Base):
    __tablename__ = "pantry--ingredient"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)

    recipes: Mapped[list["Recipe"]] = relationship(
        secondary=recipe_ingredient_assoc, back_populates="ingredients"
    )

    @property
    def recipe_ids(self) -> list[int]:
        return [recipe.id for recipe in self.recipes]

    def __repr__(self) -> str:
        return f"{self.name} (id: {self.id})"
