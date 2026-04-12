import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from frontmatter import Post
from typing import TypeVar

from mdorm.models.markdown_model import MarkdownModel

T = TypeVar("T", bound=MarkdownModel)

SECTION_PATTERN = re.compile(r"(?:^## .+\n)?<!-- section: (\w+) -->", re.MULTILINE)


@dataclass
class MetaFile:
    title: str
    mtime: float


class GenericFiles(ABC):

    @classmethod
    def _load_object(cls, Model: type[T], post: Post, title: str, mtime: float) -> T:
        specs = Model.get_field_specs()

        parts = SECTION_PATTERN.split(post.content)
        body_sections = {"content": parts[0].strip()}
        it = iter(parts[1:])
        for name, text in zip(it, it):
            body_sections[name] = text.strip()

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
        metadata = {k: v for k, v in post.metadata.items() if k not in specs}

        return Model(
            **metadata,
            **field_values,
            title=title,
            content=body_sections["content"],
            mtime=mtime,
        )

    @classmethod
    def _dump_object(cls, obj: MarkdownModel) -> Post:
        fm_fields = {}
        for name, spec in obj.__class__.get_field_specs().items():
            if spec.in_body:
                continue
            value = getattr(obj, name)
            fm_fields[name] = spec.serialize(value, name)

        sections = [obj.content] if obj.content else []
        for name, spec in obj.__class__.get_field_specs().items():
            if not spec.in_body:
                continue
            value = getattr(obj, name)
            sections.append(spec.serialize(value, name))

        return Post("\n\n".join(sections), **fm_fields)

    @abstractmethod
    def exists(self, Model: type[T], title: str) -> bool: ...

    @abstractmethod
    def read(self, Model: type[T], title: str) -> T: ...

    @abstractmethod
    def list_files(self, Model: type[T]) -> list[File]: ...

    @abstractmethod
    def write(self, obj: MarkdownModel) -> float: ...

    @abstractmethod
    def delete(self, Model: type[MarkdownModel], title: str) -> None: ...
