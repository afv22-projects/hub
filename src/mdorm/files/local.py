from pathlib import Path
from typing import TypeVar

import frontmatter

from ..models import MarkdownModel
from .generic import GenericFiles

T = TypeVar("T", bound=MarkdownModel)


class LocalFiles(GenericFiles):

    def __init__(self, models_dir: Path) -> None:
        if not models_dir.exists():
            models_dir.mkdir()

        self.models_dir = models_dir

    def exists(self, Model: type[T], title: str) -> bool:
        file = self.models_dir / Model.__name__ / (title + ".md")
        return file.exists()

    def get_mtime(self, Model: type[T], title: str) -> float | None:
        file = self.models_dir / Model.__name__ / (title + ".md")
        if not file.exists():
            return None
        return file.stat().st_mtime

    def read(self, Model: type[T], title: str) -> T:
        file = self.models_dir / Model.__name__ / (title + ".md")
        if not file.exists():
            raise FileNotFoundError()

        return self._load_object(
            Model,
            frontmatter.load(str(file)),
            file.stem,
            file.stat().st_mtime,
        )

    def list_titles(self, Model: type[T]) -> list[str]:
        model_dir = self.models_dir / Model.__name__
        if not model_dir.is_dir():
            return []
        return [path.stem for path in model_dir.iterdir()]

    def write(self, obj: MarkdownModel) -> float:
        model_dir = self.models_dir / obj.__class__.__name__
        if not model_dir.exists():
            model_dir.mkdir()

        file = model_dir / (obj.title + ".md")
        file.touch(exist_ok=True)

        post = self._dump_object(obj)
        file.write_text(frontmatter.dumps(post))
        return file.stat().st_mtime

    def delete(self, Model: type[MarkdownModel], title: str) -> None:
        file = self.models_dir / Model.__name__ / (title + ".md")
        file.unlink()
