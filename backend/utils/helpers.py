"""Miscellaneous helpers used across the backend."""

from datetime import date, timedelta
from typing import Optional


# ── Default shelf life per category (days) ────────────────────────────────────
SHELF_LIFE_MAP: dict[str, int] = {
    "dairy": 7,
    "meat": 4,
    "poultry": 3,
    "seafood": 2,
    "vegetables": 7,
    "fruits": 7,
    "bread": 5,
    "leftovers": 4,
    "frozen": 180,
    "canned": 730,
    "dry goods": 365,
    "spices": 730,
    "beverages": 30,
    "snacks": 90,
    "condiments": 180,
    "bakery": 5,
    "eggs": 21,
}


def estimate_expiry_date(
    purchase_date: date,
    category: Optional[str] = None,
    storage_location: Optional[str] = None,
) -> Optional[date]:
    """
    Estimate expiry date based on category and storage location.
    Freezer items get 10× the normal shelf life.
    """
    if not category:
        shelf_days = 7
    else:
        shelf_days = SHELF_LIFE_MAP.get(category.lower(), 7)

    if storage_location and storage_location.lower() == "freezer":
        shelf_days = min(shelf_days * 10, 365)

    return purchase_date + timedelta(days=shelf_days)


def normalize_unit(unit: str) -> str:
    """Normalize unit strings to a canonical form."""
    mapping = {
        "kg": "kg", "kilogram": "kg", "kilograms": "kg",
        "g": "g", "gram": "g", "grams": "g",
        "lb": "lb", "lbs": "lb", "pound": "lb", "pounds": "lb",
        "oz": "oz", "ounce": "oz", "ounces": "oz",
        "l": "L", "liter": "L", "liters": "L", "litre": "L", "litres": "L",
        "ml": "ml", "milliliter": "ml", "milliliters": "ml",
        "cup": "cup", "cups": "cup",
        "tbsp": "tbsp", "tablespoon": "tbsp", "tablespoons": "tbsp",
        "tsp": "tsp", "teaspoon": "tsp", "teaspoons": "tsp",
        "unit": "units", "units": "units", "piece": "units", "pieces": "units",
        "pack": "pack", "packs": "pack", "packet": "pack",
        "can": "can", "cans": "can",
        "bottle": "bottle", "bottles": "bottle",
        "bunch": "bunch", "bunches": "bunch",
        "dozen": "dozen",
    }
    return mapping.get(unit.lower().strip(), unit.strip())


def paginate(query, page: int = 1, page_size: int = 20):
    """Apply pagination to a SQLAlchemy query."""
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }
