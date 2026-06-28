from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Base


class ShoppingItemStatus(str, PyEnum):
    PENDING = "pending"
    PURCHASED = "purchased"
    SKIPPED = "skipped"


class ShoppingList(Base):
    __tablename__ = "shopping_lists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), default="Shopping List")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    owner: Mapped["User"] = relationship("User", back_populates="shopping_lists")  # noqa: F821
    items: Mapped[List["ShoppingItem"]] = relationship(
        "ShoppingItem", back_populates="shopping_list", cascade="all, delete-orphan"
    )


class ShoppingItem(Base):
    __tablename__ = "shopping_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    shopping_list_id: Mapped[int] = mapped_column(Integer, ForeignKey("shopping_lists.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, default=1.0)
    unit: Mapped[str] = mapped_column(String(50), default="units")
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    estimated_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=1)  # 1=low, 2=medium, 3=high
    reason: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)  # Why it was added
    status: Mapped[ShoppingItemStatus] = mapped_column(
        SAEnum(ShoppingItemStatus), default=ShoppingItemStatus.PENDING
    )
    is_auto_generated: Mapped[bool] = mapped_column(Boolean, default=False)

    shopping_list: Mapped["ShoppingList"] = relationship("ShoppingList", back_populates="items")
