from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum as SQLEnum

from models.pantry.item import DBItem
from enums import ConsumableCategory


class DBConsumable(DBItem):
    __tablename__ = "pantry--consumable"

    id: Mapped[int] = mapped_column(ForeignKey("pantry--item.id"), primary_key=True)
    category: Mapped[ConsumableCategory] = mapped_column(
        SQLEnum(ConsumableCategory), nullable=False, default=ConsumableCategory.OTHER
    )

    __mapper_args__ = {
        "polymorphic_identity": "consumable",
    }
