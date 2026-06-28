"""
OCR router — accepts image uploads and returns parsed receipt items.
"""

import os
import uuid
from datetime import date

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from config.database import get_db
from models.user import User
from ocr.paddle_ocr import extract_text
from ocr.receipt_parser import parse_receipt
from schemas.inventory import InventoryItemCreate
from models.inventory import StorageLocation
from utils.security import get_current_user

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}


@router.post("/scan-receipt")
async def scan_receipt(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload a grocery receipt image.
    Returns extracted items ready for inventory insertion.
    """
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {ALLOWED_EXTENSIONS}",
        )

    # Save upload temporarily
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    try:
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:  # 10 MB limit
            raise HTTPException(status_code=413, detail="File too large (max 10 MB)")
        with open(filepath, "wb") as f:
            f.write(content)

        # Extract text
        ocr_text = extract_text(filepath)
        parsed = parse_receipt(ocr_text)

        # Convert to InventoryItemCreate schemas
        items = []
        for item_data in parsed["items"]:
            items.append(
                InventoryItemCreate(
                    name=item_data["name"],
                    quantity=item_data["quantity"],
                    unit=item_data["unit"],
                    purchase_date=parsed["purchase_date"] or date.today(),
                    storage_location=StorageLocation.PANTRY,
                ).model_dump()
            )

        return {
            "purchase_date": str(parsed["purchase_date"]),
            "raw_text": ocr_text,
            "items": items,
            "item_count": len(items),
        }

    finally:
        # Clean up uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)
