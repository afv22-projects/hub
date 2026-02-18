from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String, Integer

from db import Base


class MonthlyReview(Base):
    """Represents a monthly review with key takeaways."""

    __tablename__ = "reflect--monthly_review"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # UUID
    month: Mapped[str] = mapped_column(String, nullable=False)  # "YYYY-MM"
    key_takeaway: Mapped[str] = mapped_column(String, nullable=False)
    finalized_at: Mapped[int | None] = mapped_column(Integer, nullable=True)

    def __repr__(self) -> str:
        return f"MonthlyReview(id={self.id}, month={self.month}, finalized={'Yes' if self.finalized_at else 'No'})"
