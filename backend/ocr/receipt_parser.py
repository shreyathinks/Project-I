"""
Receipt parser — extracts structured item data from OCR'd receipt text.

Strategy:
1. Identify item lines using pattern matching (price at end of line)
2. Extract quantity and unit if present (e.g. "2x Milk", "500g Pasta")
3. Parse store date from header lines
4. Return list of dicts ready to be turned into InventoryItemCreate objects
"""

import re
from datetime import date, datetime
from typing import Dict, List, Optional


# ── Regex patterns ─────────────────────────────────────────────────────────────

# Price patterns: $1.99 | 1.99 | £2.50 | €3.00
_PRICE_RE = re.compile(r"[\$£€]?\s*(\d{1,4}[.,]\d{2})\s*$")

# Quantity prefix: "2x", "3 x", "x2"
_QTY_PREFIX_RE = re.compile(r"^(\d+(?:\.\d+)?)\s*[xX]\s+(.+)$")
_QTY_WEIGHT_RE = re.compile(r"^(\d+(?:\.\d+)?)\s*(kg|g|lb|oz|ml|L|l|ltr)\s+(.+)$", re.IGNORECASE)

# Date patterns in receipts
_DATE_PATTERNS = [
    re.compile(r"\b(\d{1,2})[/\-](\d{1,2})[/\-](\d{2,4})\b"),
    re.compile(r"\b(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})\b"),
    re.compile(r"\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\b", re.IGNORECASE),
]

# Words to skip (non-item lines)
_SKIP_WORDS = {
    "subtotal", "total", "tax", "vat", "gst", "change", "cash", "credit",
    "debit", "card", "visa", "mastercard", "receipt", "thank", "you",
    "welcome", "store", "address", "phone", "tel", "fax", "www", "http",
    "manager", "cashier", "register", "terminal", "transaction",
    "discount", "coupon", "loyalty", "points", "balance", "savings",
}


def _clean_name(raw: str) -> str:
    """Remove price, codes, and extra whitespace from item name."""
    # Remove trailing price
    raw = _PRICE_RE.sub("", raw).strip()
    # Remove product codes (e.g. #1234, 0000012345)
    raw = re.sub(r"\s*#?\d{5,}\s*", " ", raw)
    # Remove asterisks, pipes
    raw = re.sub(r"[*|]", "", raw)
    return " ".join(raw.split())


def _parse_quantity_and_name(line: str) -> tuple[float, str, str]:
    """Returns (quantity, unit, cleaned_name)."""
    # Try "2x Milk" style
    m = _QTY_PREFIX_RE.match(line)
    if m:
        return float(m.group(1)), "units", _clean_name(m.group(2))

    # Try "500g Pasta" style
    m = _QTY_WEIGHT_RE.match(line)
    if m:
        return float(m.group(1)), m.group(2).lower(), _clean_name(m.group(3))

    return 1.0, "units", _clean_name(line)


def _parse_date_from_text(text: str) -> Optional[date]:
    """Extract the first recognizable date from receipt text."""
    month_map = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    }

    for pattern in _DATE_PATTERNS:
        m = pattern.search(text)
        if m:
            try:
                groups = m.groups()
                if len(groups) == 3:
                    if groups[1].lower() in month_map:
                        # "12 Jan 2024" format
                        d = int(groups[0])
                        mo = month_map[groups[1].lower()]
                        yr = int(groups[2])
                    elif len(groups[2]) == 4:
                        # "12/05/2024" — assume DD/MM/YYYY
                        d = int(groups[0])
                        mo = int(groups[1])
                        yr = int(groups[2])
                    else:
                        # "2024-05-12"
                        yr = int(groups[0])
                        mo = int(groups[1])
                        d = int(groups[2])

                    if 1 <= mo <= 12 and 1 <= d <= 31:
                        return date(yr if yr > 100 else 2000 + yr, mo, d)
            except (ValueError, IndexError):
                continue

    return None


def parse_receipt(ocr_text: str) -> Dict:
    """
    Parse OCR'd receipt text into structured data.

    Returns:
        {
            "purchase_date": date | None,
            "items": [{"name": str, "quantity": float, "unit": str}]
        }
    """
    lines = [l.strip() for l in ocr_text.splitlines() if l.strip()]
    purchase_date = _parse_date_from_text(ocr_text)
    items = []

    for line in lines:
        lower = line.lower()

        # Skip header/footer lines
        if any(skip in lower for skip in _SKIP_WORDS):
            continue

        # Skip lines that look like section headers (all caps, no price)
        if line.isupper() and not _PRICE_RE.search(line):
            continue

        # Skip very short lines
        if len(line) < 3:
            continue

        # Must have some alpha characters to be a product
        if not re.search(r"[a-zA-Z]{2,}", line):
            continue

        qty, unit, name = _parse_quantity_and_name(line)

        # Skip if name is still just numbers
        if not re.search(r"[a-zA-Z]{2,}", name):
            continue

        if name:
            items.append({
                "name": name.title(),
                "quantity": qty,
                "unit": unit,
            })

    return {
        "purchase_date": purchase_date or date.today(),
        "items": items,
    }
