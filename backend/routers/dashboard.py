"""
Dashboard router — aggregates data for the analytics dashboard.
"""

from datetime import date, timedelta
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from config.database import get_db
from models.consumption import ConsumptionRecord
from models.inventory import ExpiryStatus, InventoryItem, StorageLocation
from models.notification import Notification
from models.user import User
from utils.security import get_current_user

router = APIRouter()


@router.get("/summary")
def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Full dashboard summary for the authenticated user."""
    today = date.today()

    # ── Inventory counts ──────────────────────────────────────────────────────
    active_items = db.query(InventoryItem).filter(
        InventoryItem.user_id == current_user.id,
        InventoryItem.is_consumed == False,
    ).all()

    total = len(active_items)
    expiring_soon = sum(1 for i in active_items if i.expiry_status == ExpiryStatus.EXPIRING_SOON)
    expired = sum(1 for i in active_items if i.expiry_status == ExpiryStatus.EXPIRED)
    fresh = total - expiring_soon - expired

    by_location = {
        "refrigerator": sum(1 for i in active_items if i.storage_location == StorageLocation.REFRIGERATOR),
        "pantry": sum(1 for i in active_items if i.storage_location == StorageLocation.PANTRY),
        "freezer": sum(1 for i in active_items if i.storage_location == StorageLocation.FREEZER),
    }

    # ── Items expiring in 3 days (detail list) ────────────────────────────────
    cutoff = today + timedelta(days=3)
    expiring_detail = db.query(InventoryItem).filter(
        InventoryItem.user_id == current_user.id,
        InventoryItem.is_consumed == False,
        InventoryItem.expiry_date <= cutoff,
        InventoryItem.expiry_date >= today,
    ).order_by(InventoryItem.expiry_date.asc()).limit(10).all()

    # ── Consumption last 30 days ──────────────────────────────────────────────
    thirty_ago = today - timedelta(days=30)
    consumption_records = db.query(ConsumptionRecord).filter(
        ConsumptionRecord.user_id == current_user.id,
        ConsumptionRecord.consumed_at >= thirty_ago,
    ).all()

    items_consumed_month = len(consumption_records)

    # ── Weekly consumption trend (last 8 weeks) ───────────────────────────────
    weekly_trend = []
    for w in range(7, -1, -1):
        week_start = today - timedelta(days=today.weekday()) - timedelta(weeks=w)
        week_end = week_start + timedelta(days=6)
        count = sum(
            1 for r in consumption_records
            if week_start <= r.consumed_at.date() <= week_end
        )
        weekly_trend.append({
            "week": week_start.strftime("%b %d"),
            "consumed": count,
        })

    # ── Estimated money saved (expired items that were consumed) ─────────────
    consumed_items = db.query(InventoryItem).filter(
        InventoryItem.user_id == current_user.id,
        InventoryItem.is_consumed == True,
    ).all()
    money_saved = sum((i.price or 0) for i in consumed_items)

    # ── Unread notifications ──────────────────────────────────────────────────
    unread_notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).count()

    # ── Monthly waste (expired, not consumed) ─────────────────────────────────
    month_start = today.replace(day=1)
    wasted_this_month = db.query(InventoryItem).filter(
        InventoryItem.user_id == current_user.id,
        InventoryItem.is_consumed == False,
        InventoryItem.expiry_date < today,
        InventoryItem.expiry_date >= month_start,
    ).count()

    return {
        "inventory": {
            "total": total,
            "fresh": fresh,
            "expiring_soon": expiring_soon,
            "expired": expired,
            "by_location": by_location,
        },
        "expiring_detail": [
            {
                "id": i.id,
                "name": i.name,
                "days_until_expiry": i.days_until_expiry,
                "quantity": i.quantity,
                "unit": i.unit,
                "storage_location": i.storage_location.value,
            }
            for i in expiring_detail
        ],
        "consumption": {
            "items_consumed_last_30_days": items_consumed_month,
            "weekly_trend": weekly_trend,
        },
        "waste": {
            "wasted_this_month": wasted_this_month,
        },
        "financials": {
            "estimated_money_saved": round(money_saved, 2),
        },
        "notifications": {
            "unread_count": unread_notifications,
        },
    }


@router.get("/notifications")
def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from services.notification_service import NotificationService
    return NotificationService.get_all(db, current_user.id)


@router.post("/notifications/{notification_id}/read", status_code=204)
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from services.notification_service import NotificationService
    NotificationService.mark_read(db, current_user.id, notification_id)


@router.post("/notifications/read-all", status_code=204)
def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from services.notification_service import NotificationService
    NotificationService.mark_all_read(db, current_user.id)
