from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from models.shopping import ShoppingItemStatus


class ShoppingItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    quantity: float = Field(default=1.0, gt=0)
    unit: str = Field(default="units", max_length=50)
    category: Optional[str] = None
    estimated_price: Optional[float] = Field(default=None, ge=0)
    priority: int = Field(default=1, ge=1, le=3)
    reason: Optional[str] = None


class ShoppingItemUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[float] = Field(default=None, gt=0)
    unit: Optional[str] = None
    estimated_price: Optional[float] = None
    priority: Optional[int] = Field(default=None, ge=1, le=3)
    status: Optional[ShoppingItemStatus] = None


class ShoppingItemOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    quantity: float
    unit: str
    category: Optional[str]
    estimated_price: Optional[float]
    priority: int
    reason: Optional[str]
    status: ShoppingItemStatus
    is_auto_generated: bool


class ShoppingListCreate(BaseModel):
    name: str = Field(default="Shopping List", max_length=200)


class ShoppingListOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    is_active: bool
    items: List[ShoppingItemOut]
    created_at: datetime
    updated_at: datetime
