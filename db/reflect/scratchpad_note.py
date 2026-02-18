from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, Integer

from db import Base

if TYPE_CHECKING:
    from db.reflect import Goal


class ScratchpadNote(Base):
    """Represents a scratchpad note that can be promoted to a goal."""

    __tablename__ = "reflect--scratchpad_note"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # UUID
    text: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[int] = mapped_column(Integer, nullable=False)  # timestamp
    promoted_to_goal_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("reflect--goal.id"), nullable=True
    )

    # Relationships
    promoted_goal: Mapped["Goal | None"] = relationship(back_populates="promoted_notes")

    def __repr__(self) -> str:
        promoted = (
            f" -> Goal({self.promoted_to_goal_id})" if self.promoted_to_goal_id else ""
        )
        return f"ScratchpadNote(id={self.id}, text={self.text[:30]}...{promoted})"
