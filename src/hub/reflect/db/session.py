"""Database engine and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import configure_mappers, sessionmaker

from .base import DBBase

_engine = None
_SessionLocal = None


def init_db(db_uri: str):
    """Initialize the database engine and create all tables."""
    global _engine, _SessionLocal
    _engine = create_engine(db_uri, connect_args={"check_same_thread": False})
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    configure_mappers()
    DBBase.metadata.create_all(_engine)


def get_db():
    """Yield a database session. For use as a FastAPI dependency."""
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()