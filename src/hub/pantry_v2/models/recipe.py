from typing import Annotated

from mdorm import MarkdownModel
from mdorm.fields import (
    SectionSpec,
    ListSpec,
    ListSectionSpec,
    RelationToManySpec,
)


class Recipe(MarkdownModel):
    # Frontmatter
    labels: Annotated[list[str], ListSpec()] = []

    # Body Sections
    ingredients: Annotated[list[str], RelationToManySpec("Ingredient")] = []
    notes: Annotated[str, SectionSpec()] = ""
    sources: Annotated[list[str], ListSectionSpec()] = []
