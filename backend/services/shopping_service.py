"""
Smart shopping list service.
Combines inventory state, consumption predictions, and waste risk to
auto-generate a prioritized shopping list.
"""

from datetime import date
from typing import List

from sqlalchemy.orm import Session

from models.inventory import InventoryItem
from models.shopping import ShoppingItem, ShoppingItemStatus, ShoppingList
from schemas.shopping import ShoppingItemCreate, ShoppingListCreate


class ShoppingService:

    @staticmethod
    def get_or_create_active_list(db: Session, user_id: int) -> ShoppingList:
        lst = db.query(ShoppingList).filter(
            ShoppingList.user_id == user_id,
            ShoppingList.is_active == True,
        ).first()
        if not lst:
            lst = ShoppingList(user_id=user_id, name="My Shopping List")
            db.add(lst)
            db.commit()
            db.refresh(lst)
        return lst

    @staticmethod
    def get_lists(db: Session, user_id: int) -> List[ShoppingList]:
        return db.query(ShoppingList).filter(ShoppingList.user_id == user_id).all()

    @staticmethod
    def create_list(db: Session, user_id: int, data: ShoppingListCreate) -> ShoppingList:
        lst = ShoppingList(user_id=user_id, name=data.name)
        db.add(lst)
        db.commit()
        db.refresh(lst)
        return lst

    @staticmethod
    def add_item(
        db: Session,
        shopping_list_id: int,
        user_id: int,
        data: ShoppingItemCreate,
        is_auto: bool = False,
    ) -> ShoppingItem:
        lst = db.query(ShoppingList).filter(
            ShoppingList.id == shopping_list_id,
            ShoppingList.user_id == user_id,
        ).first()
        if not lst:
            raise ValueError("Shopping list not found")

        item = ShoppingItem(
            shopping_list_id=shopping_list_id,
            name=data.name,
            quantity=data.quantity,
            unit=data.unit,
            category=data.category,
            estimated_price=data.estimated_price,
            priority=data.priority,
            reason=data.reason,
            is_auto_generated=is_auto,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def update_item_status(
        db: Session, item_id: int, user_id: int, status: ShoppingItemStatus
    ) -> ShoppingItem:
        item = (
            db.query(ShoppingItem)
            .join(ShoppingList)
            .filter(ShoppingItem.id == item_id, ShoppingList.user_id == user_id)
            .first()
        )
        if not item:
            raise ValueError("Item not found")
        item.status = status
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete_item(db: Session, item_id: int, user_id: int) -> None:
        item = (
            db.query(ShoppingItem)
            .join(ShoppingList)
            .filter(ShoppingItem.id == item_id, ShoppingList.user_id == user_id)
            .first()
        )
        if item:
            db.delete(item)
            db.commit()

    @staticmethod
    def auto_generate(db: Session, user_id: int) -> List[ShoppingItem]:
        """
        Generate shopping items based on:
        1. Expired items (need replacement)
        2. Critically low stock (< 10% of typical quantity)
        3. Items predicted to run out soon (from prediction service)
        """
        lst = ShoppingService.get_or_create_active_list(db, user_id)

        today = date.today()
        expired = db.query(InventoryItem).filter(
            InventoryItem.user_id == user_id,
            InventoryItem.is_consumed == False,
            InventoryItem.expiry_date < today,
        ).all()

        low_stock = db.query(InventoryItem).filter(
            InventoryItem.user_id == user_id,
            InventoryItem.is_consumed == False,
            InventoryItem.quantity <= 1,
        ).all()

        added = []
        seen = {i.name.lower() for i in lst.items if i.status == ShoppingItemStatus.PENDING}

        def _add(item: InventoryItem, reason: str, priority: int):
            if item.name.lower() in seen:
                return
            seen.add(item.name.lower())
            si = ShoppingItem(
                shopping_list_id=lst.id,
                name=item.name,
                quantity=max(item.quantity * 2, 1),
                unit=item.unit,
                category=item.category_obj.name if item.category_obj else None,
                priority=priority,
                reason=reason,
                is_auto_generated=True,
            )
            db.add(si)
            added.append(si)

        for item in expired:
            _add(item, "Expired — needs replacement", priority=3)
        for item in low_stock:
            _add(item, "Low stock", priority=2)

        db.commit()
        for si in added:
            db.refresh(si)
        return added
