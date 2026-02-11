from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime, String, Integer

from models import Base


class Justification(Base):
    __tablename__ = "second_thought--justification"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    domain: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String)
    reason: Mapped[str] = mapped_column(String)
    duration: Mapped[int] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"{self.domain} ({self.ts}): {self.reason}"
