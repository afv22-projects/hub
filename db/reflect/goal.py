from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, Integer, Enum as SQLEnum

from db import Base
from enums import GoalPriority, GoalStatus

if TYPE_CHECKING:
    from db.reflect import WeeklyCheckIn, GoalMonthOutcome, ScratchpadNote


class Goal(Base):
    """Represents a goal with priority, status, and tracking."""

    __tablename__ = "reflect--goal"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # UUID
    title: Mapped[str] = mapped_column(String, nullable=False)
    priority: Mapped[GoalPriority] = mapped_column(
        SQLEnum(GoalPriority), nullable=False
    )
    exit_criteria: Mapped[str] = mapped_column(String, nullable=False)
    action_plan: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[GoalStatus] = mapped_column(SQLEnum(GoalStatus), nullable=False)
    created_at: Mapped[int] = mapped_column(Integer, nullable=False)  # timestamp
    month_created: Mapped[str] = mapped_column(String, nullable=False)  # "YYYY-MM"

    # Relationships
    weekly_check_ins: Mapped[list["WeeklyCheckIn"]] = relationship(
        back_populates="goal", cascade="all, delete-orphan"
    )
    month_outcomes: Mapped[list["GoalMonthOutcome"]] = relationship(
        back_populates="goal", cascade="all, delete-orphan"
    )
    promoted_notes: Mapped[list["ScratchpadNote"]] = relationship(
        back_populates="promoted_goal"
    )

    def __repr__(self) -> str:
        return f"Goal(id={self.id}, title={self.title}, priority={self.priority}, status={self.status})"
