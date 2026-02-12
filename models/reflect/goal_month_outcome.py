from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, Enum as SQLEnum

from models import Base
from enums import GoalOutcome

if TYPE_CHECKING:
    from models.reflect import Goal


class GoalMonthOutcome(Base):
    """Represents the outcome of a goal for a specific month."""

    __tablename__ = "reflect--goal_month_outcome"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # UUID
    goal_id: Mapped[str] = mapped_column(
        String, ForeignKey("reflect--goal.id"), nullable=False
    )
    month: Mapped[str] = mapped_column(String, nullable=False)  # "YYYY-MM"
    outcome: Mapped[GoalOutcome] = mapped_column(SQLEnum(GoalOutcome), nullable=False)
    reflection_note: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    goal: Mapped["Goal"] = relationship(back_populates="month_outcomes")

    def __repr__(self) -> str:
        return f"GoalMonthOutcome(id={self.id}, goal_id={self.goal_id}, month={self.month}, outcome={self.outcome})"
