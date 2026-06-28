"""
Expiry-checking service — called by APScheduler daily.
Creates in-app notifications and sends email alerts for:
- Items expiring in 3 days
- Items that have already expired
"""

import asyncio
import logging
from datetime import date, timedelta

from sqlalchemy.orm import Session

from config.database import SessionLocal
from models.inventory import InventoryItem
from models.notification import Notification, NotificationType
from models.user import User
from utils.email_utils import send_expiry_warning

logger = logging.getLogger(__name__)


def check_all_users_expiry():
    """Entry point called by the scheduler."""
    db: Session = SessionLocal()
    try:
        users = db.query(User).filter(User.is_active == True).all()
        for user in users:
            _process_user(db, user)
    except Exception as exc:
        logger.error("Expiry check failed: %s", exc)
    finally:
        db.close()


def _process_user(db: Session, user: User):
    today = date.today()
    warning_cutoff = today + timedelta(days=3)

    expiring_soon = db.query(InventoryItem).filter(
        InventoryItem.user_id == user.id,
        InventoryItem.is_consumed == False,
        InventoryItem.expiry_date >= today,
        InventoryItem.expiry_date <= warning_cutoff,
    ).all()

    expired = db.query(InventoryItem).filter(
        InventoryItem.user_id == user.id,
        InventoryItem.is_consumed == False,
        InventoryItem.expiry_date < today,
    ).all()

    notifications_to_add = []

    for item in expiring_soon:
        # Avoid duplicate notifications
        existing = db.query(Notification).filter(
            Notification.user_id == user.id,
            Notification.related_item_id == item.id,
            Notification.type == NotificationType.EXPIRY_WARNING,
        ).first()
        if not existing:
            notifications_to_add.append(
                Notification(
                    user_id=user.id,
                    type=NotificationType.EXPIRY_WARNING,
                    title=f"⚠️ {item.name} expires soon",
                    message=f"{item.name} expires in {item.days_until_expiry} day(s).",
                    related_item_id=item.id,
                )
            )

    for item in expired:
        existing = db.query(Notification).filter(
            Notification.user_id == user.id,
            Notification.related_item_id == item.id,
            Notification.type == NotificationType.EXPIRED,
        ).first()
        if not existing:
            notifications_to_add.append(
                Notification(
                    user_id=user.id,
                    type=NotificationType.EXPIRED,
                    title=f"🗑️ {item.name} has expired",
                    message=f"{item.name} expired on {item.expiry_date}. Remove or use immediately.",
                    related_item_id=item.id,
                )
            )

    if notifications_to_add:
        db.add_all(notifications_to_add)
        db.commit()

    # Send email if items expiring soon
    if expiring_soon and user.email:
        email_items = [
            {"name": i.name, "days_until_expiry": i.days_until_expiry}
            for i in expiring_soon
        ]
        asyncio.run(send_expiry_warning(user.email, email_items))

    logger.info(
        "User %s: %d expiring soon, %d expired",
        user.email, len(expiring_soon), len(expired)
    )
