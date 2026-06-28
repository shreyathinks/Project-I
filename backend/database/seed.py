"""
Database seeding script.
Run: python database/seed.py
Populates categories, sample users, inventory items, and loads recipes.
"""

import json
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import create_tables, SessionLocal
from models.inventory import Category, InventoryItem, StorageLocation
from models.user import User
from services.recipe_service import RecipeService
from utils.security import hash_password

CATEGORIES = [
    {"name": "Dairy", "icon": "🥛", "default_shelf_life_days": 7},
    {"name": "Meat", "icon": "🥩", "default_shelf_life_days": 4},
    {"name": "Poultry", "icon": "🍗", "default_shelf_life_days": 3},
    {"name": "Seafood", "icon": "🐟", "default_shelf_life_days": 2},
    {"name": "Vegetables", "icon": "🥦", "default_shelf_life_days": 7},
    {"name": "Fruits", "icon": "🍎", "default_shelf_life_days": 7},
    {"name": "Bread", "icon": "🍞", "default_shelf_life_days": 5},
    {"name": "Eggs", "icon": "🥚", "default_shelf_life_days": 21},
    {"name": "Frozen", "icon": "🧊", "default_shelf_life_days": 180},
    {"name": "Canned", "icon": "🥫", "default_shelf_life_days": 730},
    {"name": "Dry Goods", "icon": "🌾", "default_shelf_life_days": 365},
    {"name": "Spices", "icon": "🌶️", "default_shelf_life_days": 730},
    {"name": "Beverages", "icon": "🧃", "default_shelf_life_days": 30},
    {"name": "Snacks", "icon": "🍿", "default_shelf_life_days": 90},
    {"name": "Condiments", "icon": "🍯", "default_shelf_life_days": 180},
    {"name": "Bakery", "icon": "🥐", "default_shelf_life_days": 5},
]


def seed_categories(db):
    if db.query(Category).count() > 0:
        print("Categories already seeded.")
        return
    for cat in CATEGORIES:
        db.add(Category(**cat))
    db.commit()
    print(f"✅ Seeded {len(CATEGORIES)} categories")


def seed_demo_user(db):
    if db.query(User).filter(User.email == "demo@kitchen.app").first():
        print("Demo user already exists.")
        return

    user = User(
        email="demo@kitchen.app",
        username="demouser",
        hashed_password=hash_password("demo1234"),
        full_name="Demo User",
        household_size=2,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"✅ Created demo user: demo@kitchen.app / demo1234")

    # Seed inventory items for demo user
    today = date.today()
    categories = {c.name: c for c in db.query(Category).all()}

    sample_items = [
        InventoryItem(user_id=user.id, name="Whole Milk", quantity=2.0, unit="L",
                      purchase_date=today - timedelta(days=3),
                      expiry_date=today + timedelta(days=4),
                      storage_location=StorageLocation.REFRIGERATOR,
                      category_id=categories["Dairy"].id, price=1.50),
        InventoryItem(user_id=user.id, name="Cheddar Cheese", quantity=200, unit="g",
                      purchase_date=today - timedelta(days=1),
                      expiry_date=today + timedelta(days=14),
                      storage_location=StorageLocation.REFRIGERATOR,
                      category_id=categories["Dairy"].id, price=3.20),
        InventoryItem(user_id=user.id, name="Chicken Breast", quantity=500, unit="g",
                      purchase_date=today,
                      expiry_date=today + timedelta(days=2),
                      storage_location=StorageLocation.REFRIGERATOR,
                      category_id=categories["Poultry"].id, price=5.99),
        InventoryItem(user_id=user.id, name="Broccoli", quantity=1, unit="bunch",
                      purchase_date=today - timedelta(days=2),
                      expiry_date=today + timedelta(days=2),
                      storage_location=StorageLocation.REFRIGERATOR,
                      category_id=categories["Vegetables"].id, price=1.79),
        InventoryItem(user_id=user.id, name="Brown Rice", quantity=1000, unit="g",
                      purchase_date=today - timedelta(days=10),
                      expiry_date=today + timedelta(days=355),
                      storage_location=StorageLocation.PANTRY,
                      category_id=categories["Dry Goods"].id, price=2.49),
        InventoryItem(user_id=user.id, name="Olive Oil", quantity=500, unit="ml",
                      purchase_date=today - timedelta(days=20),
                      expiry_date=today + timedelta(days=340),
                      storage_location=StorageLocation.PANTRY,
                      category_id=categories["Condiments"].id, price=6.99),
        InventoryItem(user_id=user.id, name="Eggs", quantity=12, unit="units",
                      purchase_date=today - timedelta(days=5),
                      expiry_date=today + timedelta(days=16),
                      storage_location=StorageLocation.REFRIGERATOR,
                      category_id=categories["Eggs"].id, price=2.99),
        InventoryItem(user_id=user.id, name="Frozen Peas", quantity=400, unit="g",
                      purchase_date=today - timedelta(days=30),
                      expiry_date=today + timedelta(days=150),
                      storage_location=StorageLocation.FREEZER,
                      category_id=categories["Frozen"].id, price=1.29),
        InventoryItem(user_id=user.id, name="Sourdough Bread", quantity=1, unit="loaf",
                      purchase_date=today - timedelta(days=1),
                      expiry_date=today + timedelta(days=1),
                      storage_location=StorageLocation.PANTRY,
                      category_id=categories["Bread"].id, price=3.49),
        InventoryItem(user_id=user.id, name="Tomatoes", quantity=4, unit="units",
                      purchase_date=today - timedelta(days=4),
                      expiry_date=today + timedelta(days=3),
                      storage_location=StorageLocation.REFRIGERATOR,
                      category_id=categories["Vegetables"].id, price=1.99),
    ]

    for item in sample_items:
        db.add(item)
    db.commit()
    print(f"✅ Seeded {len(sample_items)} inventory items for demo user")


def seed_recipes(db):
    count = RecipeService.load_recipes_from_dataset(db)
    if count > 0:
        print(f"✅ Loaded {count} recipes from dataset")
    else:
        print("Recipes already loaded or dataset not found.")


if __name__ == "__main__":
    create_tables()
    db = SessionLocal()
    try:
        seed_categories(db)
        seed_demo_user(db)
        seed_recipes(db)
        print("\n🎉 Database seeded successfully!")
        print("   Login: demo@kitchen.app / demo1234")
    finally:
        db.close()
