import re
from pathlib import Path
from typing import Generator, TypeVar

import frontmatter

from .model import MarkdownModel

T = TypeVar("T", bound=MarkdownModel)

SECTION_PATTERN = re.compile(r"<!-- section: (\w+) -->")


class FileManager:

    def __init__(self, models_dir: Path) -> None:
        if not models_dir.exists():
            models_dir.mkdir()

        self.models_dir = models_dir

    @staticmethod
    def _dump_content(obj: MarkdownModel) -> str:
        """Serialize content and body fields to markdown."""
        sections = [obj.content]
        for name, spec in obj.__class__.get_field_specs().items():
            if not spec.in_body:
                continue
            value = getattr(obj, name)
            sections.append(spec.serialize(value, name))
        return "\n\n".join(sections)

    @staticmethod
    def _parse_content(content: str) -> dict[str, str]:
        """Parse markdown body into content and raw section strings."""
        parts = SECTION_PATTERN.split(content)
        sections = {"content": parts[0].strip()}
        it = iter(parts[1:])
        for name, text in zip(it, it):
            sections[name] = text.strip()
        return sections

    def _load_file(self, Model: type[T], file: Path) -> T:
        """Load a model instance from a markdown file."""
        post = frontmatter.load(str(file))
        specs = Model.get_field_specs()
        body_sections = self._parse_content(post.content)

        field_values = {}
        for name, spec in specs.items():
            if spec.in_body:
                raw = body_sections.get(name, "")
            else:
                raw = post.metadata.get(name)
                if raw is None:
                    continue
            field_values[name] = spec.deserialize(raw, name)

        # Get frontmatter fields that don't have specs (shouldn't happen, but safe)
        metadata = {
            k: v for k, v in post.metadata.items()
            if k not in specs
        }

        return Model(
            **metadata,
            **field_values,
            title=file.stem,
            content=body_sections["content"],
            mtime=file.stat().st_mtime,
        )

    def get_mtime(self, Model: type[T], title: str) -> float | None:
        file = self.models_dir / Model.__name__ / (title + ".md")
        if not file.exists():
            return None
        return file.stat().st_mtime

    def read(self, Model: type[T], title: str) -> T:
        file = self.models_dir / Model.__name__ / (title + ".md")
        if not file.exists():
            raise FileNotFoundError()
        return self._load_file(Model, file)

    def list_files(self, Model: type[T]) -> Generator[Path]:
        model_dir = self.models_dir / Model.__name__
        if model_dir.exists():
            yield from model_dir.iterdir()
        else:
            yield from ()

    def read_all(self, Model: type[T]) -> list[T]:
        return [self._load_file(Model, file) for file in self.list_files(Model)]

    def write(self, obj: MarkdownModel) -> float:
        model_dir = self.models_dir / obj.__class__.__name__
        if not model_dir.exists():
            model_dir.mkdir()

        file = model_dir / (obj.title + ".md")
        if not file.exists():
            file.touch()

        # Serialize frontmatter fields
        fm_fields = {}
        for name, spec in obj.__class__.get_field_specs().items():
            if spec.in_body:
                continue
            value = getattr(obj, name)
            fm_fields[name] = spec.serialize(value, name)

        post = frontmatter.Post(self._dump_content(obj), **fm_fields)
        file.write_text(frontmatter.dumps(post))
        return file.stat().st_mtime

    def delete(self, Model: type[MarkdownModel], title: str) -> None:
        file = self.models_dir / Model.__name__ / (title + ".md")
        if not file.exists():
            raise FileNotFoundError()

        file.unlink()
