from typing import Annotated

from hub.pantry.enums import IngredientCategory
from mdorm import MarkdownModel
from mdorm.fields import BooleanSpec, EnumSpec


class Ingredient(MarkdownModel):
    # Frontmatter
    category: Annotated[IngredientCategory, EnumSpec(IngredientCategory)] = (
        IngredientCategory.OTHER
    )
    needed: Annotated[bool, BooleanSpec()] = False
