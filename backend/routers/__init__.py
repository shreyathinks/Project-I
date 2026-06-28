from routers.auth import router as auth
from routers.inventory import router as inventory
from routers.ocr import router as ocr
from routers.barcode import router as barcode
from routers.recipes import router as recipes
from routers.shopping import router as shopping
from routers.prediction import router as prediction
from routers.dashboard import router as dashboard

__all__ = ["auth", "inventory", "ocr", "barcode", "recipes", "shopping", "prediction", "dashboard"]
