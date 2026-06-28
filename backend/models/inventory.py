from datetime import date, datetime
from enum import Enum as PyEnum
from typing import List, Optional

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Base


class StorageLocation(str, PyEnum):
    REFRIGERATOR = "refrigerator"
    PANTRY = "pantry"
    FREEZER = "freezer"


class ExpiryStatus(str, PyEnum):
    FRESH = "fresh"
    EXPIRING_SOON = "expiring_soon"  # within 3 days
    EXPIRED = "expired"


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    icon: Mapped[str] = mapped_column(String(50), nullable=True)
    default_shelf_life_days: Mapped[int] = mapped_column(Integer, default=7)

    items: Mapped[List["InventoryItem"]] = relationship("InventoryItem", back_populates="category_obj")


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)

    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    brand: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    barcode: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    quantity: Mapped[float] = mapped_column(Float, default=1.0)
    unit: Mapped[str] = mapped_column(String(50), default="units")
    purchase_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    storage_location: Mapped[StorageLocation] = mapped_column(
        SAEnum(StorageLocation), default=StorageLocation.PANTRY
    )
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_consumed: Mapped[bool] = mapped_column(Boolean, default=False)
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="inventory_items")  # noqa: F821
    category_obj: Mapped[Optional["Category"]] = relationship("Category", back_populates="items")

    @property
    def expiry_status(self) -> ExpiryStatus:
        if not self.expiry_date:
            return ExpiryStatus.FRESH
        from datetime import date as today_date
        today = today_date.today()
        delta = (self.expiry_date - today).days
        if delta < 0:
            return ExpiryStatus.EXPIRED
        if delta <= 3:
            return ExpiryStatus.EXPIRING_SOON
        return ExpiryStatus.FRESH

    @property
    def days_until_expiry(self) -> Optional[int]:
        if not self.expiry_date:
            return None
        from datetime import date as today_date
        return (self.expiry_date - today_date.today()).days
