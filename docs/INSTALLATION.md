# Installation Guide

## Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Docker Desktop | 4.x+ | Container orchestration |
| Docker Compose | 2.x+ | Multi-service management |
| Git | Any | Clone repo |
| (Optional) Ollama | Latest | Local LLM for recipe generation |

---

## Option 1 — Docker Compose (Recommended)

### Step 1: Clone and Configure

```bash
git clone <repo-url>
cd ai-kitchen-platform
cp .env.example .env
```

Edit `.env` with your settings:
- Change `SECRET_KEY` to a long random string
- (Optional) Add SMTP credentials for email notifications
- (Optional) Set `OLLAMA_HOST` if running Ollama

### Step 2: (Optional) Set Up Ollama

For AI recipe generation using a local LLM:

```bash
# Install Ollama from https://ollama.ai
ollama pull llama3.2
ollama serve
```

### Step 3: Start All Services

```bash
docker-compose up --build
```

This starts:
- PostgreSQL database on port 5432
- Redis on port 6379
- FastAPI backend on port 8000
- React frontend on port 3000
- Nginx reverse proxy on port 80

### Step 4: Seed the Database

```bash
docker-compose exec backend python database/seed.py
```

### Step 5: Load Recipes

```bash
# Via API
curl -X POST http://localhost:8000/recipes/load-dataset \
  -H "Authorization: Bearer <your-jwt-token>"

# Or visit http://localhost:8000/docs and call POST /recipes/load-dataset
```

### Access the App

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

Demo login: `demo@kitchen.app` / `demo1234`

---

## Option 2 — Local Development (without Docker)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example .env
# Edit .env with your local PostgreSQL/Redis connection strings

# Start backend
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

npm install

# Create environment file
echo "VITE_API_URL=http://localhost:8000" > .env

npm run dev
# Starts on http://localhost:5173
```

### Local Services

You need PostgreSQL and Redis running locally:

```bash
# PostgreSQL (via Docker)
docker run -d --name kitchen_db \
  -e POSTGRES_DB=kitchen_db \
  -e POSTGRES_USER=kitchen_user \
  -e POSTGRES_PASSWORD=kitchen_pass \
  -p 5432:5432 postgres:15-alpine

# Redis (via Docker)
docker run -d --name kitchen_redis \
  -p 6379:6379 redis:7-alpine
```

---

## OCR Setup (Tesseract fallback)

If PaddleOCR is not available on your platform, Tesseract is used automatically:

**Windows:**
```
Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
Add to PATH: C:\Program Files\Tesseract-OCR
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-eng
```

**macOS:**
```bash
brew install tesseract
```

---

## Train ML Models Manually

```bash
cd backend
python ml/train_models.py
```

This trains:
- Waste risk classifier (Gradient Boosting)
- Builds FAISS index for recipe embeddings

---

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | (required) | PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `SECRET_KEY` | (required) | JWT signing secret — change in production |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | JWT expiry |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama endpoint |
| `OLLAMA_MODEL` | `llama3.2` | Ollama model name |
| `SMTP_HOST` | `smtp.gmail.com` | SMTP server |
| `SMTP_PORT` | `587` | SMTP port |
| `SMTP_USER` | `""` | SMTP username |
| `SMTP_PASSWORD` | `""` | SMTP app password |
| `NOTIFICATIONS_ENABLED` | `true` | Enable email alerts |
| `OCR_ENGINE` | `paddle` | `paddle` or `tesseract` |

---

## Troubleshooting

### PaddleOCR install fails on Windows
Set `OCR_ENGINE=tesseract` in `.env` to use Tesseract instead.

### Backend crashes on startup
Check that PostgreSQL and Redis are healthy:
```bash
docker-compose ps
docker-compose logs db
docker-compose logs redis
```

### FAISS import error
```bash
pip install faiss-cpu
```

### Ollama not generating recipes
Ensure Ollama is running (`ollama serve`) and the model is pulled (`ollama pull llama3.2`).
The app works without Ollama — it will use FAISS results only.
