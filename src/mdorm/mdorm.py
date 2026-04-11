import logging
from typing import TypeVar

from .cache import Cache, Filter
from .files import GenericFiles, File
from .models import MarkdownModel, RequestBase

T = TypeVar("T", bound=MarkdownModel)


class MDorm:
    def __init__(
        self,
        files: GenericFiles,
        db_url: str = "sqlite://",
        lazy_load: bool = False,
        logger: logging.Logger | None = None,
    ):
        self.files = files
        self.cache = Cache(db_url, logger=logger)

        # Load existing objects into db
        if not lazy_load:
            for Model in MarkdownModel._registry.values():
                self._sync(Model)

    def _sync(self, Model: type[T]) -> list[File]:
        current_files = self.files.list_files(Model)
        current_titles = set(f.title for f in current_files)
        cached_titles = set(obj.title for obj in self.cache.get_rows(Model))

        for title in current_titles - cached_titles:
            obj = self.files.read(Model, title)
            self.cache.create(obj)

        for title in cached_titles - current_titles:
            self.cache.delete(Model, title)

        return current_files

    def get_or_none(self, Model: type[T], title: str) -> T | None:
        current_mtime = self.files.get_mtime(Model, title)
        cached_obj = self.cache.get_row(Model, title)

        if not current_mtime:
            if cached_obj:
                self.cache.delete(Model, title)
            return None

        if not cached_obj or cached_obj.mtime < current_mtime:
            obj = self.files.read(Model, title)
            self.cache.upsert(obj)
            return obj

        return cached_obj

    def get(self, Model: type[T], title: str) -> T:
        obj = self.get_or_none(Model, title)
        if not obj:
            raise FileNotFoundError()
        return obj

    def query(self, Model: type[T], filter: Filter | None = None) -> list[T]:
        current_files = {f.title: f.mtime for f in self._sync(Model)}
        cached_objs = self.cache.get_rows(Model, filter)
        result: list[T] = []

        for obj in cached_objs:
            if obj.mtime < current_files[obj.title]:
                obj = self.files.read(Model, obj.title)
                self.cache.upsert(obj)

            result.append(obj)

        return result

    def query_by_relation(
        self, Model: type[T], field: str, target_title: str
    ) -> list[T]:
        table = self.cache.metadata.tables[Model.__name__]
        return self.query(Model, filter=getattr(table.c, field).contains(target_title))

    def create(self, Model: type[T], obj: RequestBase | T) -> T:
        if self.files.exists(Model, obj.title):
            raise FileExistsError()
        if isinstance(obj, RequestBase):
            obj = Model(**obj.model_dump())
        mtime = self.files.write(obj)
        obj.mtime = mtime
        self.cache.create(obj)
        return obj

    def update(self, Model: type[T], obj: RequestBase | T) -> T:
        if not self.files.exists(Model, obj.title):
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
