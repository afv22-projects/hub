import time
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, Integer, Enum as SQLEnum

from hub.reflect.db import DBBase
from hub.reflect.db.mixins import VersionedMixin
from hub.reflect.enums import GoalPriority, GoalStatus

if TYPE_CHECKING:
    from hub.reflect.db import DBWeeklyCheckIn, DBGoalMonthOutcome


class DBGoal(DBBase, VersionedMixin):
    """Represents a goal with priority, status, and tracking."""

    __tablename__ = "reflect--goal"

    title: Mapped[str] = mapped_column(String, nullable=False)
    priority: Mapped[GoalPriority] = mapped_column(
        SQLEnum(GoalPriority), nullable=False
    )
    exit_criteria: Mapped[str] = mapped_column(String, nullable=False)
    action_plan: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[GoalStatus] = mapped_column(SQLEnum(GoalStatus), nullable=False)
    created_at: Mapped[int] = mapped_column(
        Integer, nullable=False, default=lambda: int(time.time() * 1000)
    )
    month_created: Mapped[str] = mapped_column(String, nullable=False)  # "YYYY-MM"

    # Relationships
    weekly_check_ins: Mapped[list["DBWeeklyCheckIn"]] = relationship(
        back_populates="goal", cascade="all, delete-orphan"
    )
    month_outcomes: Mapped[list["DBGoalMonthOutcome"]] = relationship(
        back_populates="goal", cascade="all, delete-orphan"
    )

    versioned_fields = ["title", "priority", "exit_criteria", "action_plan", "status"]

    def __repr__(self) -> str:
        return f"Goal(id={self.id}, title={self.title}, priority={self.priority}, status={self.status})"
