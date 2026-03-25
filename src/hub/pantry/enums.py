from enum import Enum


class ConsumableCategory(str, Enum):
    """Categories for organizing household consumables."""

    CLEANING = "cleaning"
    PAPER_PRODUCTS = "paper_products"
    PERSONAL_CARE = "personal_care"
    KITCHEN_SUPPLIES = "kitchen_supplies"
    BATHROOM_SUPPLIES = "bathroom_supplies"
    OTHER = "other"

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
