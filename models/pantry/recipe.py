from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String, Integer

from models import Base


class Recipe(Base):
    __tablename__ = "pantry--recipe"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    notes: Mapped[str] = mapped_column(String)

    def __repr__(self) -> str:
        return f"{self.name}"
