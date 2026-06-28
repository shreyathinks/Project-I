"""
Prediction router — exposes consumption forecasts and waste risk scoring.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from config.database import get_db
from models.inventory import InventoryItem
from models.user import User
from ml.consumption_predictor import predict_days_until_empty
from ml.waste_predictor import predict_waste_risk
from utils.security import get_current_user

router = APIRouter()


@router.get("/consumption/{item_name}")
def get_consumption_prediction(
    item_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Predict when a named item will run out based on consumption history."""
    # Get current inventory quantity for this item
    item = db.query(InventoryItem).filter(
        InventoryItem.user_id == current_user.id,
        InventoryItem.name.ilike(item_name),
        InventoryItem.is_consumed == False,
    ).first()

    current_qty = item.quantity if item else 1.0

    result = predict_days_until_empty(db, current_user.id, item_name, current_qty)
    if result is None:
        return {
            "item_name": item_name,
            "message": "Not enough consumption history to make a prediction (need ≥ 3 records)",
            "prediction": None,
        }
    return {"item_name": item_name, "prediction": result}


@router.get("/waste-risk")
def get_waste_risk(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Calculate waste risk scores for all non-consumed inventory items."""
    items = db.query(InventoryItem).filter(
        InventoryItem.user_id == current_user.id,
        InventoryItem.is_consumed == False,
    ).all()

    if not items:
        return {"items": [], "summary": {"low": 0, "medium": 0, "high": 0}}

    risks = predict_waste_risk(db, current_user.id, items)

    summary = {"low": 0, "medium": 0, "high": 0}
    for r in risks:
        summary[r["risk_level"]] += 1

    return {"items": risks, "summary": summary}


@router.get("/shopping-forecast")
def get_shopping_forecast(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return items predicted to run out within 7 days
    — used to drive smart shopping list generation.
    """
    items = db.query(InventoryItem).filter(
        InventoryItem.user_id == current_user.id,
        InventoryItem.is_consumed == False,
    ).all()

    forecasts = []
    for item in items:
        result = predict_days_until_empty(db, current_user.id, item.name, item.quantity)
        if result and result["days_remaining"] <= 7:
            forecasts.append({
                "item_id": item.id,
                "item_name": item.name,
                "current_quantity": item.quantity,
                "unit": item.unit,
                **result,
            })

    forecasts.sort(key=lambda x: x["days_remaining"])
    return {"items_to_restock": forecasts}
