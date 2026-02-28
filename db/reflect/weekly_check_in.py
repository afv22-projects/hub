import time
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, Integer, Enum as SQLEnum

from db import Base
from enums import TrackingStatus

if TYPE_CHECKING:
    from db.reflect import DBGoal


class DBWeeklyCheckIn(Base):
    """Represents a weekly check-in for a goal."""

    __tablename__ = "reflect--weekly_check_in"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    goal_id: Mapped[str] = mapped_column(
        String, ForeignKey("reflect--goal.id"), nullable=False
    )
    week_of: Mapped[str] = mapped_column(
        String, nullable=False
    )  # ISO date of the Monday
    tracking_status: Mapped[TrackingStatus] = mapped_column(
        SQLEnum(TrackingStatus), nullable=False
    )
    reflection_note: Mapped[str] = mapped_column(String, nullable=False)
    strategy_adjustment: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[int] = mapped_column(
        Integer, nullable=False, default=lambda: int(time.time() * 1000)
    )  # timestamp in milliseconds

    # Relationships
    goal: Mapped["DBGoal"] = relationship(back_populates="weekly_check_ins")

    def __repr__(self) -> str:
        return f"WeeklyCheckIn(id={self.id}, goal_id={self.goal_id}, week_of={self.week_of}, status={self.tracking_status})"
