from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from config.database import get_db
from models.inventory import ExpiryStatus, StorageLocation
from models.user import User
from schemas.inventory import CategoryOut, ConsumeItem, InventoryItemCreate, InventoryItemOut, InventoryItemUpdate
from services.inventory_service import InventoryService
from utils.security import get_current_user

router = APIRouter()


@router.get("/", response_model=List[InventoryItemOut])
def list_items(
    storage_location: Optional[StorageLocation] = Query(default=None),
    category_id: Optional[int] = Query(default=None),
    expiry_status: Optional[ExpiryStatus] = Query(default=None),
    search: Optional[str] = Query(default=None, max_length=100),
    include_consumed: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all inventory items with optional filters."""
    return InventoryService.get_items(
        db, current_user.id, storage_location, category_id, expiry_status, search, include_consumed
    )


@router.post("/", response_model=InventoryItemOut, status_code=201)
def create_item(
    data: InventoryItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a new inventory item."""
    return InventoryService.create_item(db, current_user.id, data)


@router.post("/bulk", response_model=List[InventoryItemOut], status_code=201)
def bulk_create(
    items: List[InventoryItemCreate],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add multiple inventory items at once (used by OCR receipt scanner)."""
    return InventoryService.bulk_add_items(db, current_user.id, items)


@router.get("/expiring", response_model=List[InventoryItemOut])
def expiring_soon(
    days: int = Query(default=3, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get items expiring within the next N days."""
    return InventoryService.get_expiring_items(db, current_user.id, days)


@router.get("/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    """List all food categories."""
    return InventoryService.get_categories(db)


@router.get("/{item_id}", response_model=InventoryItemOut)
def get_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return InventoryService.get_item(db, current_user.id, item_id)


@router.put("/{item_id}", response_model=InventoryItemOut)
def update_item(
    item_id: int,
    data: InventoryItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return InventoryService.update_item(db, current_user.id, item_id, data)


@router.delete("/{item_id}", status_code=204)
def delete_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    InventoryService.delete_item(db, current_user.id, item_id)


@router.post("/{item_id}/consume", response_model=InventoryItemOut)
def consume(
    item_id: int,
    data: ConsumeItem,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Record consumption of an item — decreases quantity and logs for prediction."""
    return InventoryService.consume_item(db, current_user.id, item_id, data.quantity_consumed)
