"""
In-app notification service.
"""

from typing import List

from sqlalchemy.orm import Session

from models.notification import Notification


class NotificationService:

    @staticmethod
    def get_unread(db: Session, user_id: int) -> List[Notification]:
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
        ).order_by(Notification.created_at.desc()).all()

    @staticmethod
    def get_all(db: Session, user_id: int, limit: int = 50) -> List[Notification]:
        return db.query(Notification).filter(
            Notification.user_id == user_id,
        ).order_by(Notification.created_at.desc()).limit(limit).all()

    @staticmethod
    def mark_read(db: Session, user_id: int, notification_id: int) -> None:
        notif = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        ).first()
        if notif:
            notif.is_read = True
            db.commit()

    @staticmethod
    def mark_all_read(db: Session, user_id: int) -> None:
        db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
        ).update({"is_read": True})
        db.commit()
