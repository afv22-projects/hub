from enum import Enum


class IngredientCategory(str, Enum):
    """Categories for organizing pantry ingredients."""

    DAIRY = "dairy"
    MEAT = "meat"
    PRODUCE = "produce"
    GRAINS = "grains"
    SPICES = "spices"
    CONDIMENTS = "condiments"
    CANNED = "canned"
    FROZEN = "frozen"
    BAKERY = "bakery"
    BEVERAGES = "beverages"
    SNACKS = "snacks"
    OTHER = "other"
