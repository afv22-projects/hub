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


# Sort order for grocery list display - adjust numbers to match your store's layout
CATEGORY_SORT_ORDER = {
    IngredientCategory.PRODUCE: 1,
    IngredientCategory.BAKERY: 2,
    IngredientCategory.MEAT: 3,
    IngredientCategory.CONDIMENTS: 4,
    IngredientCategory.SPICES: 5,
    IngredientCategory.CANNED: 6,
    IngredientCategory.SNACKS: 7,
    IngredientCategory.BEVERAGES: 8,
    ConsumableCategory.PAPER_PRODUCTS: 9,
    ConsumableCategory.KITCHEN_SUPPLIES: 10,
    ConsumableCategory.CLEANING: 11,
    IngredientCategory.DAIRY: 12,
    IngredientCategory.GRAINS: 13,
    IngredientCategory.FROZEN: 14,
    ConsumableCategory.BATHROOM_SUPPLIES: 15,
    ConsumableCategory.PERSONAL_CARE: 16,
}
