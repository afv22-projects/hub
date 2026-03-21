import re

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

import sqlalchemy as db
from sqlalchemy.sql.type_api import TypeEngine as TypeEngine


class FieldSpec(ABC):
    """Base class for field specifications.

    Each field spec defines:
    - Where the field is stored (frontmatter vs body)
    - How to serialize/deserialize the value
    - The database column type
    - Optional relation target model
    """

    in_body: bool = False
    target_model: str | None = None

    @property
    @abstractmethod
    def db_type(self) -> db.types.TypeEngine:
        """SQLAlchemy column type for this field."""
        ...

    def serialize(self, value: Any, field_name: str) -> Any:
        """Convert Python value to markdown representation."""
        return value

    def deserialize(self, value: Any, field_name: str) -> Any:
        """Convert markdown representation to Python value."""
        return value


class BooleanSpec(FieldSpec):
    """BooleanSpec field stored in frontmatter."""

    @property
    def db_type(self) -> db.types.TypeEngine:
        return db.Boolean()


class EnumSpec(FieldSpec):
    """EnumSpec field stored in frontmatter."""

    def __init__(self, EnumType: type[Enum]) -> None:
        self.EnumType = EnumType

    @property
    def db_type(self) -> TypeEngine:
        return db.Enum(self.EnumType)

    def serialize(self, value: Enum, field_name: str) -> str:
        return value.value

    def deserialize(self, value: str, field_name: str) -> Enum:
        return self.EnumType(value)


class IntegerSpec(FieldSpec):
    """IntegerSpec field stored in frontmatter."""

    @property
    def db_type(self) -> db.types.TypeEngine:
        return db.Integer()


class StringSpec(FieldSpec):
    """String field stored in frontmatter."""

    def __init__(self, max_length: int = 255):
        self.max_length = max_length

    @property
    def db_type(self) -> db.types.TypeEngine:
        return db.String(self.max_length)


class SectionMixin:

    def _format_heading(self, field_name: str) -> str:
        return field_name.replace("_", " ").title()

    def _serialize(self, value: str, field_name: str) -> str:
        heading = self._format_heading(field_name)
        return f"## {heading}\n<!-- section: {field_name} -->\n\n{value}"


class SectionSpec(FieldSpec, SectionMixin):
    """Text field stored as a section in the markdown body."""

    in_body = True

    @property
    def db_type(self) -> db.types.TypeEngine:
        return db.Text()

    def serialize(self, value: str, field_name: str) -> str:
        return self._serialize(value, field_name)


class ListSpec(FieldSpec):
    """List of strings stored as comma-separated string in frontmatter."""

    @property
    def db_type(self) -> db.types.TypeEngine:
        return db.JSON()

    def serialize(self, value: list[str], field_name: str) -> str:
        return ", ".join(value)

    def deserialize(self, value: str, field_name: str) -> list[str]:
        return [item.strip() for item in value.split(",") if item]


class ListSectionSpec(FieldSpec, SectionMixin):
    """List of strings stored as bullet list in body section."""

    in_body = True

    @property
    def db_type(self) -> db.types.TypeEngine:
        return db.JSON()

    def serialize(self, value: list[str], field_name: str) -> str:
        content = "\n".join(f"- {item}" for item in value)
        return self._serialize(content, field_name)

    def deserialize(self, value: str, field_name: str) -> list[str]:
        lines = value.strip().split("\n") if value else []
        return [line.lstrip("- ").strip() for line in lines if line.strip()]


class RelationMixin:

    WIKI_LINK_PATTERN = re.compile(r"\[\[([^/\]]+)/([^\]]+)\]\]")

    def __init__(self, target: str):
        self.target_model = target

    def _create_link(self, title) -> str:
        return f"[[{self.target_model}/{title}]]"

    def _parse_match(self, match: re.Match[str]) -> str:
        found_model, found_title = match.group(1), match.group(2)
        if found_model != self.target_model:
            raise ValueError(
                f"Expected [[{self.target_model}/...]] but found [[{found_model}/...]]"
            )
        return found_title


class RelationToOneSpec(FieldSpec, RelationMixin):
    """
    Single relation stored as wiki-link in frontmatter.
    usage example: Annotated[str, RelationToOneSpec("Author")]
    """

    @property
    def db_type(self) -> db.types.TypeEngine:
        return db.String(255)

    def serialize(self, value: str, field_name: str) -> str:
        return self._create_link(value)

    def deserialize(self, value: str, field_name: str) -> str:
        match = self.WIKI_LINK_PATTERN.match(str(value))
        if not match:
            raise ValueError(f"Invalid wiki-link format: {value}")

        return self._parse_match(match)


class RelationToManySpec(ListSectionSpec, RelationMixin):
    """Multiple relations stored as wiki-link list in body section.
    usage example: Annotated[str, RelationToManySpec("Author")]
    """

    def serialize(self, value: list[str], field_name: str) -> str:
        links = [self._create_link(title) for title in value]
        return super().serialize(links, field_name)

    def deserialize(self, value: str, field_name: str) -> list[str]:
        return [
            self._parse_match(match) for match in self.WIKI_LINK_PATTERN.finditer(value)
        ]


def get_field_spec(metadata: list) -> FieldSpec | None:
    """Extract FieldSpec from Annotated type metadata."""
    for item in metadata:
        if isinstance(item, FieldSpec):
            return item
    return None
