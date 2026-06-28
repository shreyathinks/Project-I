from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.database import get_db
from models.shopping import ShoppingItemStatus
from models.user import User
from schemas.shopping import ShoppingItemCreate, ShoppingItemUpdate, ShoppingItemOut, ShoppingListCreate, ShoppingListOut
from services.shopping_service import ShoppingService
from utils.security import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ShoppingListOut])
def get_lists(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ShoppingService.get_lists(db, current_user.id)


@router.post("/", response_model=ShoppingListOut, status_code=201)
def create_list(
    data: ShoppingListCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ShoppingService.create_list(db, current_user.id, data)


@router.post("/auto-generate", response_model=List[ShoppingItemOut])
def auto_generate(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Auto-generate shopping items from expired/low stock inventory."""
    return ShoppingService.auto_generate(db, current_user.id)


@router.post("/{list_id}/items", response_model=ShoppingItemOut, status_code=201)
def add_item(
    list_id: int,
    data: ShoppingItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return ShoppingService.add_item(db, list_id, current_user.id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/items/{item_id}", response_model=ShoppingItemOut)
def update_item(
    item_id: int,
    data: ShoppingItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        if data.status:
            return ShoppingService.update_item_status(db, item_id, current_user.id, data.status)
        raise HTTPException(status_code=400, detail="Provide status to update")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/items/{item_id}", status_code=204)
def delete_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ShoppingService.delete_item(db, item_id, current_user.id)
