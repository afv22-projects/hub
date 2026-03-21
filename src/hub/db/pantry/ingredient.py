from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum as SQLEnum

from .item import DBItem
from .recipe_ingredient_assoc import recipe_ingredient_assoc
from hub.enums import IngredientCategory

if TYPE_CHECKING:
    from hub.db.pantry import DBRecipe


class DBIngredient(DBItem):
    __tablename__ = "pantry--ingredient"

    id: Mapped[str] = mapped_column(ForeignKey("pantry--item.id"), primary_key=True)
    category: Mapped[IngredientCategory] = mapped_column(
        SQLEnum(IngredientCategory), nullable=False, default=IngredientCategory.OTHER
    )

    __mapper_args__ = {
        "polymorphic_identity": "ingredient",
    }

    recipes: Mapped[list["DBRecipe"]] = relationship(
        secondary=recipe_ingredient_assoc, back_populates="ingredients"
    )

    @property
    def recipe_ids(self) -> list[str]:
        return [recipe.id for recipe in self.recipes]
