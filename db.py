import os

from sqlalchemy import create_engine


DB_URI = os.environ.get("DB_URI", "sqlite:///:memory:")

engine = create_engine(DB_URI)
