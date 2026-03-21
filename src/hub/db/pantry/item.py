from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Boolean, String

from hub.db import DBBase


class DBItem(DBBase):
    """Base class for all pantry items (ingredients, consumables, etc.)."""

    __tablename__ = "pantry--item"

    name: Mapped[str] = mapped_column(String, unique=True)
    needed: Mapped[bool] = mapped_column(Boolean, default=False)
    type: Mapped[str] = mapped_column(String(50))

    __mapper_args__ = {
        "polymorphic_on": "type",
    }

    def __repr__(self) -> str:
        return f"{self.name} (id: {self.id})"
