# Architecture Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Docker Compose Network                            │
│                                                                             │
│  ┌──────────────┐    ┌──────────────────────────────────────────────────┐  │
│  │              │    │                  Nginx (Port 80)                  │  │
│  │   Browser    │───▶│  /api/* → backend:8000 | /* → frontend:80       │  │
│  │              │    └──────────────────────────────────────────────────┘  │
│  └──────────────┘           │                        │                     │
│                             ▼                        ▼                     │
│                   ┌──────────────────┐    ┌──────────────────┐            │
│                   │ FastAPI Backend  │    │  React Frontend  │            │
│                   │   Port 8000      │    │    Port 3000      │            │
│                   │                  │    │  Vite + Tailwind  │            │
│                   └────────┬─────────┘    └──────────────────┘            │
│                            │                                               │
│              ┌─────────────┼─────────────┐                                │
│              ▼             ▼             ▼                                 │
│   ┌──────────────┐ ┌────────────┐ ┌────────────────────────┐             │
│   │  PostgreSQL  │ │   Redis    │ │  Ollama (host machine) │             │
│   │  Port 5432   │ │ Port 6379  │ │  Port 11434            │             │
│   └──────────────┘ └────────────┘ └────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Backend Layer Architecture

```
HTTP Request
    │
    ▼
┌─────────────────────────────────┐
│  FastAPI Router (thin layer)    │  ← validates input, calls service
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  Service Layer (business logic) │  ← all business rules, orchestration
└──────┬──────────┬───────────────┘
       │          │
       ▼          ▼
┌──────────┐ ┌──────────┐
│  SQLAlch │ │   ML /   │
│  ORM +   │ │   OCR    │
│  Models  │ │  Modules │
└──────────┘ └──────────┘
```

## ER Diagram

```
┌──────────────────┐       ┌─────────────────────────────────────────┐
│      users       │       │             inventory_items              │
├──────────────────┤  1:N  ├─────────────────────────────────────────┤
│ id (PK)          │◄──────│ id (PK)                                  │
│ email (unique)   │       │ user_id (FK → users.id)                 │
│ username (unique)│       │ category_id (FK → categories.id)        │
│ hashed_password  │       │ name                                     │
│ full_name        │       │ brand, barcode                          │
│ is_active        │       │ quantity, unit                          │
│ household_size   │       │ purchase_date, expiry_date              │
│ dietary_prefs    │       │ storage_location (enum)                 │
│ created_at       │       │ is_consumed, price                      │
└──────────────────┘       └─────────────────────────────────────────┘
         │                              │
         │ 1:N                          │ N:1
         ▼                              ▼
┌──────────────────┐       ┌─────────────────┐
│  shopping_lists  │       │   categories    │
├──────────────────┤       ├─────────────────┤
│ id (PK)          │       │ id (PK)         │
│ user_id (FK)     │       │ name (unique)   │
│ name             │       │ icon            │
│ is_active        │       │ shelf_life_days │
└────────┬─────────┘       └─────────────────┘
         │ 1:N
         ▼
┌──────────────────────┐
│    shopping_items    │
├──────────────────────┤
│ id (PK)              │
│ shopping_list_id(FK) │
│ name, quantity, unit │
│ category, priority   │
│ reason, status(enum) │
│ is_auto_generated    │
└──────────────────────┘

┌────────────────────────────┐      ┌──────────────────────────────┐
│      notifications         │      │     consumption_records      │
├────────────────────────────┤      ├──────────────────────────────┤
│ id (PK)                    │      │ id (PK)                      │
│ user_id (FK)               │      │ user_id (FK)                 │
│ type (enum)                │      │ item_name                    │
│ title, message             │      │ category                     │
│ is_read, is_email_sent     │      │ quantity_consumed            │
│ related_item_id            │      │ unit                         │
│ created_at                 │      │ consumed_at                  │
└────────────────────────────┘      └──────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                         recipes                          │
├─────────────────────────────────────────────────────────┤
│ id (PK)                                                  │
│ title, description                                       │
│ ingredients (JSON text), instructions                    │
│ cooking_time_minutes, servings                          │
│ cuisine, category                                        │
│ is_vegetarian, is_vegan, is_high_protein, is_gluten_free│
│ calories, protein_g                                      │
│ source_url, image_url                                    │
└─────────────────────────────────────────────────────────┘
```

## ML Pipeline

```
Inventory Items
       │
       ├─── Waste Risk Prediction
       │         │
       │    Features: [days_until_expiry, quantity, avg_daily,
       │               shelf_life_pct, days_since_purchase]
       │         │
       │    Scikit-learn GradientBoostingClassifier
       │         │
       │    Output: low | medium | high + score
       │
       ├─── Consumption Prediction
       │         │
       │    ConsumptionRecord history
       │         │
       │    Facebook Prophet (≥3 records) or Linear fallback
       │         │
       │    Output: days_remaining, restock_date, confidence
       │
       └─── Recipe Recommendation
                 │
            Inventory ingredient names
                 │
            SentenceTransformers (all-MiniLM-L6-v2)
            → embed ingredient query
                 │
            FAISS IndexFlatIP (cosine similarity)
            → top-K recipe candidates
                 │
            Optional: Ollama LLM → generated recipe text
```

## Data Flow: Receipt Scanning

```
User uploads image
        │
        ▼
POST /ocr/scan-receipt
        │
        ▼
PaddleOCR (or Tesseract fallback)
→ raw text
        │
        ▼
receipt_parser.py
→ regex extraction of:
   - item names (alpha-containing lines with prices)
   - quantities (2x, 500g patterns)
   - purchase date
        │
        ▼
Returns list of InventoryItemCreate objects
        │
        ▼
User reviews/edits items in UI
        │
        ▼
POST /inventory/bulk
→ Items added to database
```

## Security Architecture

- Passwords hashed with bcrypt (via passlib)
- JWTs signed with HS256 using `SECRET_KEY` from environment
- All protected routes require valid JWT via `get_current_user` dependency
- File uploads limited to 10 MB and validated by extension
- Rate limiting via Nginx (`limit_req_zone`)
- Security headers set by Nginx (X-Frame-Options, X-Content-Type-Options)
- No secrets stored in code — all from environment variables
- CORS configured to allow only known frontend origins

## Folder Structure

```
ai-kitchen-platform/
├── backend/
│   ├── config/          # settings.py (Pydantic), database.py (SQLAlchemy engine)
│   ├── models/          # SQLAlchemy ORM models (one file per domain entity)
│   ├── schemas/         # Pydantic v2 request/response models
│   ├── routers/         # FastAPI routers (thin HTTP handlers)
│   ├── services/        # Business logic (one file per domain)
│   ├── ml/              # ML models: Prophet, scikit-learn, FAISS
│   ├── ocr/             # OCR wrapper (PaddleOCR + Tesseract) and parser
│   ├── utils/           # security.py, email_utils.py, helpers.py
│   ├── database/        # seed.py for dev/demo data
│   ├── scheduler/       # APScheduler task definitions
│   └── main.py          # FastAPI app factory
├── frontend/
│   └── src/
│       ├── api/         # Axios API client modules (one per resource)
│       ├── components/  # Reusable UI components
│       ├── pages/       # Route-level page components
│       ├── context/     # React Context (AuthContext)
│       └── utils/       # Frontend helpers
├── datasets/            # recipes.json, products.json, categories.json
├── docker/              # nginx.conf, postgres/init.sql
└── docs/                # INSTALLATION.md, API.md, ARCHITECTURE.md
```
