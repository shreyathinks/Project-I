from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base


class Recipe(Base):
    """
    Stores recipe data — populated from datasets/recipes.json at startup
    and used for FAISS-based similarity search.
    """
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ingredients: Mapped[str] = mapped_column(Text, nullable=False)  # JSON list
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    cooking_time_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    servings: Mapped[int] = mapped_column(Integer, default=2)
    cuisine: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Dietary flags
    is_vegetarian: Mapped[bool] = mapped_column(Integer, default=0)
    is_vegan: Mapped[bool] = mapped_column(Integer, default=0)
    is_high_protein: Mapped[bool] = mapped_column(Integer, default=0)
    is_gluten_free: Mapped[bool] = mapped_column(Integer, default=0)

    # Nutrition (optional)
    calories: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    protein_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Source / attribution
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
