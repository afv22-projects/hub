import logging
from contextlib import contextmanager
from typing import TypeVar

import sqlalchemy as db
from sqlalchemy.pool import StaticPool

from .model import MarkdownModel


T = TypeVar("T", bound=MarkdownModel)
type Filter = db.ColumnElement[bool]


class Cache:
    def __init__(self, db_url: str = "sqlite://", logger: logging.Logger | None = None):
        if logger:
            sql_logger = logging.getLogger("sqlalchemy.engine")
            sql_logger.setLevel(logger.level)
            sql_logger.handlers = logger.handlers
            sql_logger.propagate = False

        # Use StaticPool for in-memory SQLite to keep the same connection alive
        # across all operations, preventing data loss between requests
        if db_url in ("sqlite://", "sqlite:///:memory:"):
            self.engine = db.create_engine(
                db_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            self.engine = db.create_engine(db_url)
        self.metadata = db.MetaData()

        # Initialize tables
        for Model in MarkdownModel._registry.values():
            columns: list[db.Column] = [
                db.Column("title", db.String(255), primary_key=True),
                db.Column("content", db.Text),
                db.Column("mtime", db.Float),
            ]
            for name, spec in Model.get_field_specs().items():
                column = db.Column(name, spec.db_type)
                columns.append(column)

            db.Table(Model.__name__, self.metadata, *columns)

        self.metadata.create_all(self.engine)

    @contextmanager
    def _connect(self, Model: type[MarkdownModel]):
        table = self.metadata.tables[Model.__name__]
        with self.engine.connect() as conn:
            yield conn, table
            conn.commit()

    def get_row(self, Model: type[T], title: str) -> T | None:
        with self._connect(Model) as (conn, table):
            row = conn.execute(table.select().where(table.c.title == title)).fetchone()
        return Model(**row._mapping) if row else None

    def get_rows(self, Model: type[T], filter: Filter | None = None) -> list[T]:
        with self._connect(Model) as (conn, table):
            query = table.select()
            if filter is not None:
                query = query.where(filter)
            rows = conn.execute(query).fetchall()
        return [Model(**row._mapping) for row in rows]

    def create(self, obj: MarkdownModel) -> None:
        with self._connect(obj.__class__) as (conn, table):
            conn.execute(table.insert().values(obj.model_dump()))

    def update(self, obj: MarkdownModel) -> None:
        with self._connect(obj.__class__) as (conn, table):
            result = conn.execute(
                table.update()
                .where(table.c.title == obj.title)
                .values(**obj.model_dump())
            )
            if result.rowcount == 0:
                raise FileNotFoundError()

    def upsert(self, obj: MarkdownModel) -> None:
        with self._connect(obj.__class__) as (conn, table):
            data = obj.model_dump()
            result = conn.execute(
                table.update().where(table.c.title == obj.title).values(**data)
            )
            if result.rowcount == 0:
                conn.execute(table.insert().values(data))

    def delete(self, Model: type[MarkdownModel], title: str) -> None:
        with self._connect(Model) as (conn, table):
            result = conn.execute(table.delete().where(table.c.title == title))
            if result.rowcount == 0:
                raise FileNotFoundError()
