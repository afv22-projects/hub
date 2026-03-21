from pathlib import Path
from typing import TypeVar

from .cache import Cache
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
                for obj in self.files.read_all(Model):
                    self.cache.create(obj)

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

    def get(self, model: type[T], title: str) -> T:
        obj = self.get_or_none(model, title)
        if not obj:
            raise FileNotFoundError()
        return obj

    def all(self, Model: type[T]) -> list[T]:
        return [
            obj
            for title in self.files.list_files(Model)
            if (obj := self.get_or_none(Model, title.stem))
        ]

    def create(self, obj: MarkdownModel) -> None:
        mtime = self.files.write(obj)
        obj.mtime = mtime
        self.cache.create(obj)

    def update(self, obj: MarkdownModel) -> None:
        mtime = self.files.write(obj)
        obj.mtime = mtime
        self.cache.update(obj)

    def delete(self, Model: type[MarkdownModel], title: str) -> None:
        self.files.delete(Model, title)
        self.cache.delete(Model, title)
