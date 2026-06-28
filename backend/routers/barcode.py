"""
Barcode lookup router.
Searches a local products dataset for a barcode, then optionally
falls back to the Open Food Facts API (free, no key required).
"""

import json
import logging
import os
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Cache of local product DB
_products_db: dict = {}


def _load_products():
    global _products_db
    if _products_db:
        return
    path = os.path.join(settings.datasets_dir, "products.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            products = json.load(f)
        _products_db = {p["barcode"]: p for p in products}
        logger.info("Loaded %d products from dataset", len(_products_db))


class ProductInfo(BaseModel):
    barcode: str
    name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    source: str = "local"


@router.get("/lookup/{barcode}", response_model=ProductInfo)
async def lookup_barcode(barcode: str):
    """
    Look up a product by barcode.
    Checks local dataset first; falls back to Open Food Facts API.
    """
    _load_products()

    # 1. Local dataset lookup
    if barcode in _products_db:
        p = _products_db[barcode]
        return ProductInfo(
            barcode=barcode,
            name=p.get("name", "Unknown"),
            brand=p.get("brand"),
            category=p.get("category"),
            unit=p.get("unit", "units"),
            source="local",
        )

    # 2. Open Food Facts (free, no API key needed)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == 1:
                    product = data["product"]
                    return ProductInfo(
                        barcode=barcode,
                        name=product.get("product_name") or product.get("product_name_en", "Unknown"),
                        brand=product.get("brands"),
                        category=product.get("categories", "").split(",")[0].strip() or None,
                        unit="units",
                        source="open_food_facts",
                    )
    except Exception as exc:
        logger.warning("Open Food Facts lookup failed: %s", exc)

    raise HTTPException(
        status_code=404,
        detail="Product not found. Please enter details manually.",
    )
