import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.base import Base


DB_URI = os.environ.get("DB_URI", "sqlite:///./app.db")

engine = create_engine(DB_URI, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
