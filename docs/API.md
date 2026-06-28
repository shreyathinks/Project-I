# API Documentation

All endpoints require a `Bearer` JWT token in the `Authorization` header unless marked as public.

Interactive documentation available at `http://localhost:8000/docs` (Swagger UI).

---

## Authentication — `/auth`

### POST `/auth/register` — Public
Register a new user.

**Request:**
```json
{
  "email": "user@example.com",
  "username": "janesmith",
  "password": "securepassword",
  "full_name": "Jane Smith",
  "household_size": 2
}
```

**Response:** `201 Created`
```json
{ "id": 1, "email": "user@example.com", "username": "janesmith", ... }
```

---

### POST `/auth/login` — Public
Authenticate and receive a JWT.

**Request:**
```json
{ "email": "user@example.com", "password": "securepassword" }
```

**Response:**
```json
{ "access_token": "eyJ...", "token_type": "bearer", "user": { ... } }
```

---

### GET `/auth/me` — Protected
Return the authenticated user's profile.

### PUT `/auth/me` — Protected
Update profile fields: `full_name`, `household_size`, `dietary_preferences`.

---

## Inventory — `/inventory`

### GET `/inventory/` — Protected
List all inventory items. Query parameters:
- `storage_location`: `refrigerator | pantry | freezer`
- `category_id`: integer
- `expiry_status`: `fresh | expiring_soon | expired`
- `search`: string
- `include_consumed`: boolean (default `false`)

### POST `/inventory/` — Protected
Create an inventory item. Expiry date is auto-estimated if omitted.

### POST `/inventory/bulk` — Protected
Create multiple items at once (used by OCR).

### GET `/inventory/expiring` — Protected
Get items expiring in N days (default 3).

### GET `/inventory/categories` — Public
List all food categories.

### GET `/inventory/{id}` — Protected
Get a single item.

### PUT `/inventory/{id}` — Protected
Update an item.

### DELETE `/inventory/{id}` — Protected
Delete an item.

### POST `/inventory/{id}/consume` — Protected
Record consumption. Body: `{ "quantity_consumed": 1.5 }`

---

## OCR — `/ocr`

### POST `/ocr/scan-receipt` — Protected
Upload a receipt image (multipart/form-data, field `file`).

**Response:**
```json
{
  "purchase_date": "2024-01-15",
  "raw_text": "...",
  "items": [
    { "name": "Whole Milk", "quantity": 1.0, "unit": "units", "storage_location": "pantry", "purchase_date": "2024-01-15" }
  ],
  "item_count": 12
}
```

---

## Barcode — `/barcode`

### GET `/barcode/lookup/{barcode}` — Public
Look up product info by barcode. Checks local dataset first, then Open Food Facts.

**Response:**
```json
{
  "barcode": "5000112637922",
  "name": "Tropicana Orange Juice 1L",
  "brand": "Tropicana",
  "category": "Beverages",
  "unit": "bottle",
  "source": "local"
}
```

---

## Recipes — `/recipes`

### GET `/recipes/` — Public
Browse all recipes. Query params: `search`, `vegetarian`, `vegan`, `limit`.

### POST `/recipes/recommend` — Protected
Get AI recommendations based on inventory.

**Request:**
```json
{
  "available_ingredients": ["chicken", "broccoli", "garlic"],
  "filter_vegetarian": false,
  "filter_vegan": false,
  "filter_high_protein": true,
  "max_cooking_time": 30,
  "use_expiring_first": true,
  "top_k": 5
}
```

**Response:**
```json
{
  "recipes": [ { "id": 1, "title": "Chicken Stir-Fry", ... } ],
  "generated_recipe": "...",
  "source": "ollama"
}
```

### GET `/recipes/{id}` — Public
Get a single recipe.

### POST `/recipes/load-dataset` — Protected
Load recipes from `datasets/recipes.json` into the database.

---

## Shopping — `/shopping`

### GET `/shopping/` — Protected
List all shopping lists.

### POST `/shopping/` — Protected
Create a new list.

### POST `/shopping/auto-generate` — Protected
Auto-generate shopping items from expired/low-stock inventory.

### POST `/shopping/{list_id}/items` — Protected
Add an item to a list.

### PATCH `/shopping/items/{item_id}` — Protected
Update item status: `pending | purchased | skipped`.

### DELETE `/shopping/items/{item_id}` — Protected
Delete a shopping item.

---

## Prediction — `/prediction`

### GET `/prediction/consumption/{item_name}` — Protected
Predict days until an item runs out.

**Response:**
```json
{
  "item_name": "Milk",
  "prediction": {
    "days_remaining": 5,
    "restock_date": "2024-01-20",
    "avg_daily_consumption": 0.4,
    "confidence": "high",
    "method": "prophet"
  }
}
```

### GET `/prediction/waste-risk` — Protected
Get waste risk scores for all active inventory items.

**Response:**
```json
{
  "items": [
    {
      "item_id": 1,
      "item_name": "Broccoli",
      "risk_level": "high",
      "risk_score": 0.87,
      "days_until_expiry": 1,
      "quantity": 1.0
    }
  ],
  "summary": { "low": 5, "medium": 3, "high": 2 }
}
```

### GET `/prediction/shopping-forecast` — Protected
Get items predicted to run out within 7 days.

---

## Dashboard — `/dashboard`

### GET `/dashboard/summary` — Protected
Full dashboard summary: inventory counts, expiring items, consumption trends, financials, notification count.

### GET `/dashboard/notifications` — Protected
Get all notifications for the user.

### POST `/dashboard/notifications/{id}/read` — Protected
Mark a notification as read.

### POST `/dashboard/notifications/read-all` — Protected
Mark all notifications as read.

---

## Health Check

### GET `/health` — Public
```json
{ "status": "ok", "version": "1.0.0" }
```
