from enum import Enum


class IngredientCategory(str, Enum):
    """Categories for organizing pantry ingredients."""

    DAIRY = "Dairy"
    MEAT = "Meat"
    PRODUCE = "Produce"
    GRAINS = "Grains"
    SPICES = "Spices"
    CONDIMENTS = "Condiments"
    CANNED = "Canned"
    FROZEN = "Frozen"
    BAKERY = "Bakery"
    BEVERAGES = "Beverages"
    SNACKS = "Snacks"
    OTHER = "Other"
