import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DB_URI = os.environ.get("DB_URI", "sqlite:///./app.db")
engine = create_engine(DB_URI, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase): ...


def init_db():
    # Import all models so they're registered with Base.metadata
    from db.second_thought import (
        Justification,
    )
    from db.pantry import (
        DBConsumable,
        DBIngredient,
        DBItem,
        DBRecipe,
    )
    from db.reflect import (
        Goal,
        WeeklyCheckIn,
        GoalMonthOutcome,
        MonthlyReview,
        ScratchpadNote,
    )

    Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
