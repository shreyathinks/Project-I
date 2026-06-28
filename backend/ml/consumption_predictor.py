"""
Consumption Predictor — uses Facebook Prophet to forecast
when a given food item will run out.

Prophet models are persisted to disk so re-training only happens
when new consumption data is available.
"""

import logging
import os
import pickle
from datetime import datetime, timedelta
from typing import Dict, Optional

import pandas as pd
from sqlalchemy.orm import Session

from config.settings import settings
from models.consumption import ConsumptionRecord

logger = logging.getLogger(__name__)

MODELS_DIR = os.path.join(settings.models_cache_dir, "prophet")
os.makedirs(MODELS_DIR, exist_ok=True)


def _model_path(user_id: int, item_name: str) -> str:
    safe_name = "".join(c if c.isalnum() else "_" for c in item_name.lower())
    return os.path.join(MODELS_DIR, f"u{user_id}_{safe_name}.pkl")


def train_model(db: Session, user_id: int, item_name: str) -> Optional[object]:
    """Train a Prophet model for a specific user + item combination."""
    records = (
        db.query(ConsumptionRecord)
        .filter(
            ConsumptionRecord.user_id == user_id,
            ConsumptionRecord.item_name.ilike(item_name),
        )
        .order_by(ConsumptionRecord.consumed_at.asc())
        .all()
    )

    if len(records) < 3:
        logger.info("Not enough data to train Prophet for %s (need ≥ 3 records)", item_name)
        return None

    df = pd.DataFrame(
        [{"ds": r.consumed_at, "y": r.quantity_consumed} for r in records]
    )
    # Aggregate by day
    df["ds"] = pd.to_datetime(df["ds"]).dt.normalize()
    df = df.groupby("ds", as_index=False)["y"].sum()

    try:
        from prophet import Prophet
        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=False,
            changepoint_prior_scale=0.3,
        )
        model.fit(df)

        with open(_model_path(user_id, item_name), "wb") as f:
            pickle.dump(model, f)

        return model
    except Exception as exc:
        logger.error("Prophet training failed for %s: %s", item_name, exc)
        return None


def predict_days_until_empty(
    db: Session,
    user_id: int,
    item_name: str,
    current_quantity: float,
) -> Optional[Dict]:
    """
    Predict how many days until the item runs out.
    Returns a dict with 'days_remaining', 'restock_date', 'confidence'.
    """
    path = _model_path(user_id, item_name)

    # Try loading persisted model; retrain if not available
    model = None
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                model = pickle.load(f)
        except Exception:
            pass

    if model is None:
        model = train_model(db, user_id, item_name)

    if model is None:
        # Simple linear fallback: avg daily consumption from records
        records = (
            db.query(ConsumptionRecord)
            .filter(
                ConsumptionRecord.user_id == user_id,
                ConsumptionRecord.item_name.ilike(item_name),
            )
            .all()
        )
        if not records:
            return None

        total_consumed = sum(r.quantity_consumed for r in records)
        days_span = max(
            (records[-1].consumed_at - records[0].consumed_at).days, 1
        )
        avg_daily = total_consumed / days_span
        if avg_daily <= 0:
            return None

        days_remaining = round(current_quantity / avg_daily)
        restock_date = (datetime.now() + timedelta(days=days_remaining)).date()
        return {
            "days_remaining": days_remaining,
            "restock_date": str(restock_date),
            "avg_daily_consumption": round(avg_daily, 3),
            "confidence": "low",
            "method": "linear_fallback",
        }

    # Use Prophet forecast
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)
    future_only = forecast[forecast["ds"] >= pd.Timestamp.now()]

    cumulative = 0.0
    days_remaining = None
    for _, row in future_only.iterrows():
        cumulative += max(row["yhat"], 0)
        if cumulative >= current_quantity:
            days_remaining = int((row["ds"] - pd.Timestamp.now()).days)
            break

    if days_remaining is None:
        days_remaining = 30  # More than a month worth

    restock_date = (datetime.now() + timedelta(days=days_remaining)).date()
    avg_daily = future_only["yhat"].clip(lower=0).mean()

    return {
        "days_remaining": days_remaining,
        "restock_date": str(restock_date),
        "avg_daily_consumption": round(avg_daily, 3),
        "confidence": "high",
        "method": "prophet",
    }
