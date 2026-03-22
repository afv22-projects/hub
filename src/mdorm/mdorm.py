from pathlib import Path
from typing import TypeVar

from .cache import Cache, Filter
from .file_manager import FileManager
from .model import MarkdownModel

T = TypeVar("T", bound=MarkdownModel)


class MDorm:
    def __init__(
        self,
        models_dir: Path,
        db_url: str = "sqlite://",
        lazy_load: bool = False,
    ):
        self.files = FileManager(models_dir)
        self.cache = Cache(db_url)

        # Load existing objects into db
        if not lazy_load:
            for Model in MarkdownModel._registry.values():
                self._sync(Model)

    def _sync(self, Model: type[T]) -> None:
        current_titles = set(file.stem for file in self.files.list_files(Model))
        cached_titles = set(obj.title for obj in self.cache.get_rows(Model))

        for title in current_titles - cached_titles:
            obj = self.files.read(Model, title)
            self.cache.create(obj)

        for title in cached_titles - current_titles:
            self.cache.delete(Model, title)

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
        self._sync(Model)
        cached_objs = self.cache.get_rows(Model, filter)
        result: list[T] = []

        for obj in cached_objs:
            current_mtime = self.files.get_mtime(Model, obj.title)
            if not current_mtime:
                self.cache.delete(Model, obj.title)
                continue

            if obj.mtime < current_mtime:
                obj = self.files.read(Model, obj.title)
                self.cache.upsert(obj)

            result.append(obj)

        return result

    def create(self, obj: MarkdownModel) -> None:
        if self.files.exists(obj.__class__, obj.title):
            raise FileExistsError()
        mtime = self.files.write(obj)
        obj.mtime = mtime
        self.cache.create(obj)

    def update(self, obj: MarkdownModel) -> None:
        if not self.files.exists(obj.__class__, obj.title):
            raise FileNotFoundError()
        mtime = self.files.write(obj)
        obj.mtime = mtime
        self.cache.update(obj)

    def upsert(self, obj: MarkdownModel) -> None:
        mtime = self.files.write(obj)
        obj.mtime = mtime
        self.cache.upsert(obj)

    def delete(self, Model: type[MarkdownModel], title: str) -> None:
        self.files.delete(Model, title)
        self.cache.delete(Model, title)
