# AI Kitchen Intelligence Platform

A production-ready, AI-powered web application for kitchen inventory management, food waste reduction, and intelligent recipe/shopping recommendations. Built entirely with free and open-source technologies.

## Features

- **Inventory Management** — Track items across Fridge, Pantry, and Freezer
- **OCR Receipt Scanner** — Upload grocery receipts to auto-populate inventory (PaddleOCR)
- **Barcode Scanner** — Scan product barcodes for instant lookup (QuaggaJS)
- **Expiry Tracking** — Color-coded freshness indicators with daily background checks
- **AI Recipe Recommendations** — FAISS + SentenceTransformers with optional Ollama LLM
- **Consumption Prediction** — Prophet-powered forecasts for restocking timing
- **Smart Shopping List** — Auto-generated lists from predictions and low stock
- **Waste Risk Prediction** — Scikit-learn model scoring waste risk per item
- **Analytics Dashboard** — Recharts-powered charts for trends and insights
- **JWT Authentication** — Secure register/login with user profiles
- **Email Notifications** — SMTP alerts for expiring items
- **Fully Dockerized** — Runs locally with Docker Compose

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18 + Vite, Tailwind CSS, React Router v6, Recharts |
| Backend | FastAPI, SQLAlchemy 2.0, Pydantic v2, APScheduler |
| Database | PostgreSQL 15, Redis 7 |
| ML / AI | Prophet, Scikit-learn, SentenceTransformers, FAISS, Ollama (Llama 3.2) |
| OCR | PaddleOCR (primary), Tesseract (fallback) |
| Barcode | QuaggaJS |
| Deployment | Docker, Docker Compose, Nginx |

## Quick Start

### Prerequisites

- Docker Desktop (or Docker + Docker Compose)
- Git
- (Optional) [Ollama](https://ollama.ai) installed locally for LLM features

### 1. Clone and Configure

```bash
git clone <repo-url>
cd ai-kitchen-platform
cp .env.example .env
# Edit .env with your settings (SMTP, secrets, etc.)
```

### 2. (Optional) Start Ollama with Llama 3.2

```bash
ollama pull llama3.2
ollama serve
```

### 3. Launch with Docker Compose

```bash
docker-compose up --build
```

### 4. Access the Application

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

### 5. Seed Sample Data

```bash
docker-compose exec backend python database/seed.py
```

## Development Setup (without Docker)

See [docs/INSTALLATION.md](docs/INSTALLATION.md) for local development setup.

## Project Structure

```
ai-kitchen-platform/
├── backend/                  # FastAPI application
│   ├── config/               # Settings and database connection
│   ├── models/               # SQLAlchemy ORM models
│   ├── schemas/              # Pydantic request/response schemas
│   ├── routers/              # API route handlers (thin layer)
│   ├── services/             # Business logic
│   ├── ml/                   # Machine learning models and training
│   ├── ocr/                  # OCR processing
│   ├── utils/                # Security, email, helpers
│   ├── database/             # Migrations and seed scripts
│   └── scheduler/            # APScheduler background tasks
├── frontend/                 # React + Vite application
│   └── src/
│       ├── api/              # Axios API client modules
│       ├── components/       # Reusable UI components
│       ├── pages/            # Route-level page components
│       ├── context/          # React Context providers
│       └── utils/            # Frontend helpers
├── datasets/                 # Sample recipes, products, categories
├── docs/                     # Documentation
│   ├── INSTALLATION.md
│   ├── API.md
│   └── ARCHITECTURE.md
└── docker/                   # Docker support files
    ├── nginx.conf
    └── postgres/
        └── init.sql
```

## API Documentation

Full API reference: [docs/API.md](docs/API.md)

Interactive Swagger UI available at `http://localhost:8000/docs` when running.

## Environment Variables

See [.env.example](.env.example) for all configurable options.

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for ER diagrams and system design.

## License

MIT License - free to use, modify, and distribute.
