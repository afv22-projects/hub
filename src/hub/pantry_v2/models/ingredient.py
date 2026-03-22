from typing import Annotated

from hub.enums import IngredientCategory
from mdorm import MarkdownModel
from mdorm.fields import EnumSpec


class Ingredient(MarkdownModel):
    # Frontmatter
    category: Annotated[IngredientCategory, EnumSpec(IngredientCategory)]
