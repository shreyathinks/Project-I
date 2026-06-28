from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Base


class ConsumptionRecord(Base):
    """
    Tracks each time a quantity of an item is consumed.
    Used by Prophet to predict future consumption patterns.
    """
    __tablename__ = "consumption_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    item_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    quantity_consumed: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), default="units")
    consumed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="consumption_records")  # noqa: F821
