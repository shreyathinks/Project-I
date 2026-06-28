from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from models.inventory import ExpiryStatus, StorageLocation


class CategoryOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    icon: Optional[str]
    default_shelf_life_days: int


class InventoryItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    brand: Optional[str] = None
    barcode: Optional[str] = None
    quantity: float = Field(default=1.0, gt=0)
    unit: str = Field(default="units", max_length=50)
    purchase_date: date
    expiry_date: Optional[date] = None
    storage_location: StorageLocation = StorageLocation.PANTRY
    category_id: Optional[int] = None
    notes: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0)


class InventoryItemUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    brand: Optional[str] = None
    quantity: Optional[float] = Field(default=None, gt=0)
    unit: Optional[str] = None
    purchase_date: Optional[date] = None
    expiry_date: Optional[date] = None
    storage_location: Optional[StorageLocation] = None
    category_id: Optional[int] = None
    notes: Optional[str] = None
    price: Optional[float] = None
    is_consumed: Optional[bool] = None


class InventoryItemOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    brand: Optional[str]
    barcode: Optional[str]
    quantity: float
    unit: str
    purchase_date: date
    expiry_date: Optional[date]
    storage_location: StorageLocation
    category_id: Optional[int]
    category_obj: Optional[CategoryOut] = None
    notes: Optional[str]
    is_consumed: bool
    price: Optional[float]
    expiry_status: ExpiryStatus
    days_until_expiry: Optional[int]
    created_at: datetime
    updated_at: datetime


class ConsumeItem(BaseModel):
    quantity_consumed: float = Field(..., gt=0)


class InventoryFilter(BaseModel):
    storage_location: Optional[StorageLocation] = None
    category_id: Optional[int] = None
    expiry_status: Optional[ExpiryStatus] = None
    search: Optional[str] = None
