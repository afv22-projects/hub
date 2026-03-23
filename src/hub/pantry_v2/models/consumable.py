from typing import Annotated

from hub.enums import ConsumableCategory
from mdorm import MarkdownModel
from mdorm.fields import BooleanSpec, EnumSpec


class Consumable(MarkdownModel):
    # Frontmatter
    category: Annotated[ConsumableCategory, EnumSpec(ConsumableCategory)] = (
        ConsumableCategory.OTHER
    )
    needed: Annotated[bool, BooleanSpec()] = False
