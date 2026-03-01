import os
import uuid

from sqlalchemy import String, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    configure_mappers,
    mapped_column,
    sessionmaker,
)
from sqlalchemy_history import make_versioned
from sqlalchemy_history.plugins import PropertyModTrackerPlugin

# Initialize versioning before models are defined
# user_cls=None disables user tracking since we don't have a User model
make_versioned(
    user_cls=None,  # type: ignore
    plugins=[PropertyModTrackerPlugin()],
)

DB_URI = os.environ.get("DB_URI", "sqlite:///./app.db")
engine = create_engine(DB_URI, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class DBBase(DeclarativeBase):
    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )


def init_db():
    configure_mappers()
    DBBase.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
