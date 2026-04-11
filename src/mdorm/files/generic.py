import re
from abc import ABC, abstractmethod
from typing import TypeVar

from mdorm.models.markdown_model import MarkdownModel

T = TypeVar("T", bound=MarkdownModel)

SECTION_PATTERN = re.compile(r"(?:^## .+\n)?<!-- section: (\w+) -->", re.MULTILINE)


class GenericFiles(ABC):

    @staticmethod
    def _dump_content(obj: MarkdownModel) -> str:
        """Serialize content and body fields to markdown."""
        sections = [obj.content] if obj.content else []
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

    @abstractmethod
    def exists(self, Model: type[T], title: str) -> bool: ...

    @abstractmethod
    def get_mtime(self, Model: type[T], title: str) -> float | None: ...

    @abstractmethod
    def read(self, Model: type[T], title: str) -> T: ...

    @abstractmethod
    def list_titles(self, Model: type[T]) -> list[str]: ...

    @abstractmethod
    def write(self, obj: MarkdownModel) -> float: ...

    @abstractmethod
    def delete(self, Model: type[MarkdownModel], title: str) -> None: ...
