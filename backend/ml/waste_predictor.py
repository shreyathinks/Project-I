"""
Waste Risk Predictor — uses a scikit-learn RandomForestClassifier
to predict the waste risk level (low / medium / high) for each
inventory item.

Features:
- days_until_expiry
- quantity_remaining
- avg_daily_consumption (from consumption records or default)
- shelf_life_pct_remaining  (days_until_expiry / total_shelf_life)
- days_since_purchase
"""

import logging
import os
import pickle
from datetime import date
from typing import Dict, List, Optional

import numpy as np
from sqlalchemy.orm import Session

from config.settings import settings
from models.inventory import InventoryItem
from models.consumption import ConsumptionRecord

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(settings.models_cache_dir, "waste_predictor.pkl")
os.makedirs(settings.models_cache_dir, exist_ok=True)

RISK_LABELS = {0: "low", 1: "medium", 2: "high"}


def _build_features(item: InventoryItem, avg_daily: float) -> List[float]:
    today = date.today()
    days_until_expiry = item.days_until_expiry if item.days_until_expiry is not None else 30
    days_since_purchase = (today - item.purchase_date).days if item.purchase_date else 0

    if item.expiry_date and item.purchase_date:
        total_shelf_life = max((item.expiry_date - item.purchase_date).days, 1)
        shelf_life_pct_remaining = max(days_until_expiry / total_shelf_life, 0)
    else:
        shelf_life_pct_remaining = 1.0

    return [
        days_until_expiry,
        item.quantity,
        avg_daily,
        shelf_life_pct_remaining,
        days_since_purchase,
    ]


def _get_avg_daily(db: Session, user_id: int, item_name: str) -> float:
    records = (
        db.query(ConsumptionRecord)
        .filter(
            ConsumptionRecord.user_id == user_id,
            ConsumptionRecord.item_name.ilike(item_name),
        )
        .all()
    )
    if not records or len(records) < 2:
        return 0.3  # Default: consumes ~0.3 units/day

    total = sum(r.quantity_consumed for r in records)
    days = max((records[-1].consumed_at - records[0].consumed_at).days, 1)
    return total / days


def _load_or_create_model():
    """Load saved model or create and save a default one."""
    if os.path.exists(MODEL_PATH):
        try:
            with open(MODEL_PATH, "rb") as f:
                return pickle.load(f)
        except Exception:
            pass

    # Create a lightweight default model with synthetic training data
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline

    # Synthetic training data based on domain knowledge
    # Features: [days_until_expiry, quantity, avg_daily, shelf_life_pct, days_since_purchase]
    X = np.array([
        # High risk
        [1, 5.0, 0.1, 0.05, 25], [0, 3.0, 0.2, 0.0, 20], [-1, 2.0, 0.1, 0.0, 30],
        [2, 10.0, 0.1, 0.08, 28], [1, 1.0, 0.5, 0.03, 15],
        # Medium risk
        [4, 5.0, 0.5, 0.3, 10], [5, 8.0, 0.8, 0.4, 12], [3, 2.0, 0.3, 0.25, 18],
        [6, 6.0, 0.4, 0.35, 14], [4, 3.0, 0.6, 0.28, 16],
        # Low risk
        [14, 5.0, 1.0, 0.7, 5], [21, 3.0, 0.8, 0.8, 3], [30, 2.0, 0.5, 0.9, 1],
        [10, 8.0, 2.0, 0.6, 7], [20, 10.0, 1.5, 0.85, 4],
    ])
    y = np.array([2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0])

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(n_estimators=50, random_state=42)),
    ])
    model.fit(X, y)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    return model


_model = None


def predict_waste_risk(
    db: Session,
    user_id: int,
    items: List[InventoryItem],
) -> List[Dict]:
    global _model
    if _model is None:
        _model = _load_or_create_model()

    results = []
    for item in items:
        avg_daily = _get_avg_daily(db, user_id, item.name)
        features = _build_features(item, avg_daily)
        X = np.array([features])
        risk_idx = int(_model.predict(X)[0])
        probas = _model.predict_proba(X)[0]

        results.append({
            "item_id": item.id,
            "item_name": item.name,
            "risk_level": RISK_LABELS[risk_idx],
            "risk_score": round(float(probas[risk_idx]), 3),
            "days_until_expiry": item.days_until_expiry,
            "quantity": item.quantity,
        })

    return results
