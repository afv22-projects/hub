import logging
from typing import TypeVar

from .cache import Cache, Filter
from .files import GenericFiles
from .models import MarkdownModel, RequestBase

T = TypeVar("T", bound=MarkdownModel)


class MDorm:
    def __init__(
        self,
        files: GenericFiles,
        db_url: str = "sqlite://",
        logger: logging.Logger | None = None,
    ):
        self.files = files
        self.cache = Cache(db_url, logger=logger)
        self.sync()

    def sync(self):
        for Model in MarkdownModel._registry.values():
            current_files = self.files.list_files(Model)
            current_titles = set(f.title for f in current_files)
            cached_objs = {obj.title: obj for obj in self.cache.get_rows(Model)}

            # Create new files
            for title in current_titles - cached_objs.keys():
                obj = self.files.read(Model, title)
                self.cache.create(obj)

            # Delete removed files
            for title in cached_objs.keys() - current_titles:
                self.cache.delete(Model, title)

            # Update stale files
            for f in current_files:
                cached = cached_objs.get(f.title)
                if cached and cached.mtime < f.mtime:
                    obj = self.files.read(Model, f.title)
                    self.cache.upsert(obj)

    def get_or_none(self, Model: type[T], title: str) -> T | None:
        return self.cache.get_row(Model, title)

    def get(self, Model: type[T], title: str) -> T:
        obj = self.get_or_none(Model, title)
        if not obj:
            raise FileNotFoundError()
        return obj

    def query(self, Model: type[T], filter: Filter | None = None) -> list[T]:
        return self.cache.get_rows(Model, filter)

    def query_by_relation(
        self, Model: type[T], field: str, target_title: str
    ) -> list[T]:
        table = self.cache.metadata.tables[Model.__name__]
        return self.query(Model, filter=getattr(table.c, field).contains(target_title))

    def create(self, Model: type[T], obj: RequestBase | T) -> T:
        if self.cache.get_row(Model, obj.title):
            raise FileExistsError()
        if isinstance(obj, RequestBase):
            obj = Model(**obj.model_dump())
        mtime = self.files.write(obj)
        obj.mtime = mtime
        self.cache.create(obj)
        return obj

    def update(self, Model: type[T], obj: RequestBase | T) -> T:
        if not self.cache.get_row(Model, obj.title):
            raise FileNotFoundError()
        if isinstance(obj, RequestBase):
            obj = Model(**obj.model_dump())
        mtime = self.files.write(obj)
        obj.mtime = mtime
        self.cache.update(obj)
        return obj

    def upsert(self, Model: type[T], obj: RequestBase | T) -> None:
        if isinstance(obj, RequestBase):
            obj = Model(**obj.model_dump())
        mtime = self.files.write(obj)
        obj.mtime = mtime
        self.cache.upsert(obj)

    def delete(self, Model: type[MarkdownModel], title: str) -> None:
        self.files.delete(Model, title)
        self.cache.delete(Model, title)
