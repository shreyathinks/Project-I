from datetime import date
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.inventory import Category, InventoryItem, StorageLocation, ExpiryStatus
from models.consumption import ConsumptionRecord
from schemas.inventory import InventoryItemCreate, InventoryItemUpdate
from utils.helpers import estimate_expiry_date


class InventoryService:

    @staticmethod
    def get_items(
        db: Session,
        user_id: int,
        storage_location: Optional[StorageLocation] = None,
        category_id: Optional[int] = None,
        expiry_status: Optional[ExpiryStatus] = None,
        search: Optional[str] = None,
        include_consumed: bool = False,
    ) -> List[InventoryItem]:
        query = db.query(InventoryItem).filter(
            InventoryItem.user_id == user_id,
            InventoryItem.is_consumed == include_consumed,
        )
        if storage_location:
            query = query.filter(InventoryItem.storage_location == storage_location)
        if category_id:
            query = query.filter(InventoryItem.category_id == category_id)
        if search:
            query = query.filter(InventoryItem.name.ilike(f"%{search}%"))

        items = query.order_by(InventoryItem.expiry_date.asc().nullslast()).all()

        if expiry_status:
            items = [i for i in items if i.expiry_status == expiry_status]

        return items

    @staticmethod
    def get_item(db: Session, user_id: int, item_id: int) -> InventoryItem:
        item = db.query(InventoryItem).filter(
            InventoryItem.id == item_id,
            InventoryItem.user_id == user_id,
        ).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item

    @staticmethod
    def create_item(db: Session, user_id: int, data: InventoryItemCreate) -> InventoryItem:
        # Auto-estimate expiry date if not provided
        expiry = data.expiry_date
        if not expiry:
            category_name = None
            if data.category_id:
                cat = db.query(Category).filter(Category.id == data.category_id).first()
                if cat:
                    category_name = cat.name
            expiry = estimate_expiry_date(
                data.purchase_date,
                category=category_name,
                storage_location=data.storage_location.value if data.storage_location else None,
            )

        item = InventoryItem(
            user_id=user_id,
            name=data.name,
            brand=data.brand,
            barcode=data.barcode,
            quantity=data.quantity,
            unit=data.unit,
            purchase_date=data.purchase_date,
            expiry_date=expiry,
            storage_location=data.storage_location,
            category_id=data.category_id,
            notes=data.notes,
            price=data.price,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def update_item(db: Session, user_id: int, item_id: int, data: InventoryItemUpdate) -> InventoryItem:
        item = InventoryService.get_item(db, user_id, item_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete_item(db: Session, user_id: int, item_id: int) -> None:
        item = InventoryService.get_item(db, user_id, item_id)
        db.delete(item)
        db.commit()

    @staticmethod
    def consume_item(db: Session, user_id: int, item_id: int, quantity: float) -> InventoryItem:
        item = InventoryService.get_item(db, user_id, item_id)
        if quantity > item.quantity:
            raise HTTPException(status_code=400, detail="Cannot consume more than available quantity")

        item.quantity -= quantity
        if item.quantity <= 0:
            item.quantity = 0
            item.is_consumed = True

        # Log consumption for prediction
        record = ConsumptionRecord(
            user_id=user_id,
            item_name=item.name,
            category=item.category_obj.name if item.category_obj else None,
            quantity_consumed=quantity,
            unit=item.unit,
        )
        db.add(record)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def get_expiring_items(db: Session, user_id: int, days: int = 3) -> List[InventoryItem]:
        from datetime import date, timedelta
        cutoff = date.today() + timedelta(days=days)
        return db.query(InventoryItem).filter(
            InventoryItem.user_id == user_id,
            InventoryItem.is_consumed == False,
            InventoryItem.expiry_date <= cutoff,
            InventoryItem.expiry_date >= date.today(),
        ).all()

    @staticmethod
    def get_categories(db: Session) -> List[Category]:
        return db.query(Category).all()

    @staticmethod
    def bulk_add_items(db: Session, user_id: int, items: List[InventoryItemCreate]) -> List[InventoryItem]:
        created = []
        for data in items:
            created.append(InventoryService.create_item(db, user_id, data))
        return created
