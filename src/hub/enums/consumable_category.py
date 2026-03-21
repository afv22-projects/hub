from enum import Enum


class ConsumableCategory(str, Enum):
    """Categories for organizing household consumables."""

    CLEANING = "cleaning"
    PAPER_PRODUCTS = "paper_products"
    PERSONAL_CARE = "personal_care"
    KITCHEN_SUPPLIES = "kitchen_supplies"
    BATHROOM_SUPPLIES = "bathroom_supplies"
    OTHER = "other"
