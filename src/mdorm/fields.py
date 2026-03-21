from abc import ABC, abstractmethod
from typing import Any
import re

import sqlalchemy as db


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


class SectionMixin(FieldSpec):

    in_body = True

    @property
    def db_type(self) -> db.types.TypeEngine:
        return db.Text()

    def _serialize(self, value: str, field_name: str) -> str:
        return f"<!-- section: {field_name} -->\n\n{value}"


class SectionSpec(SectionMixin):
    """Text field stored as a section in the markdown body."""

    def serialize(self, value: str, field_name: str) -> str:
        return self._serialize(value, field_name)

    def deserialize(self, value: str, field_name: str) -> str:
        return value


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


class RelationToOne(FieldSpec, RelationMixin):
    """
    Single relation stored as wiki-link in frontmatter.
    usage example: Annotated[str, RelationToOne("Author")]
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


class RelationToMany(SectionMixin, RelationMixin):
    """Multiple relations stored as wiki-link list in body section.
    usage example: Annotated[str, RelationToMany("Author")]
    """

    def serialize(self, value: list[str], field_name: str) -> str:
        links = [f"- {self._create_link(title)}" for title in value]
        content = "\n".join(links)
        return self._serialize(content, field_name)

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
