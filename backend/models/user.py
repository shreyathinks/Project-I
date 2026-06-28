from datetime import datetime
from typing import List

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    household_size: Mapped[int] = mapped_column(Integer, default=1)
    dietary_preferences: Mapped[str] = mapped_column(String(500), nullable=True)  # JSON string
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    inventory_items: Mapped[List["InventoryItem"]] = relationship(  # noqa: F821
        "InventoryItem", back_populates="owner", cascade="all, delete-orphan"
    )
    shopping_lists: Mapped[List["ShoppingList"]] = relationship(  # noqa: F821
        "ShoppingList", back_populates="owner", cascade="all, delete-orphan"
    )
    notifications: Mapped[List["Notification"]] = relationship(  # noqa: F821
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
    consumption_records: Mapped[List["ConsumptionRecord"]] = relationship(  # noqa: F821
        "ConsumptionRecord", back_populates="user", cascade="all, delete-orphan"
    )
