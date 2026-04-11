from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generator, TypeVar

from mdorm.models.markdown_model import MarkdownModel

T = TypeVar("T", bound=MarkdownModel)


class GenericFiles(ABC):

    @abstractmethod
    def exists(self, Model: type[T], title: str) -> bool: ...

    @abstractmethod
    def get_mtime(self, Model: type[T], title: str) -> float | None: ...

    @abstractmethod
    def read(self, Model: type[T], title: str) -> T: ...

    @abstractmethod
    def list_files(self, Model: type[T]) -> Generator[Path]: ...

    @abstractmethod
    def write(self, obj: MarkdownModel) -> float: ...

    @abstractmethod
    def delete(self, Model: type[MarkdownModel], title: str) -> None: ...
