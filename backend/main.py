"""
AI Kitchen Intelligence Platform — FastAPI entry point.
All routers are registered here; business logic lives in services/.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config.database import create_tables
from config.settings import settings
from routers import auth, inventory, ocr, barcode, recipes, shopping, prediction, dashboard
from scheduler.tasks import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle hooks."""
    # Create DB tables (Alembic handles migrations in prod; this covers dev)
    create_tables()
    # Start APScheduler background jobs
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="AI Kitchen Intelligence Platform",
    description=(
        "Manage your kitchen inventory, reduce food waste, and get AI-powered "
        "recipe and shopping recommendations. Powered by FastAPI, Prophet, "
        "SentenceTransformers, FAISS, and optional Ollama LLM."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files for uploads ──────────────────────────────────────────────────
import os
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth,       prefix="/auth",       tags=["Authentication"])
app.include_router(inventory,  prefix="/inventory",  tags=["Inventory"])
app.include_router(ocr,        prefix="/ocr",        tags=["OCR"])
app.include_router(barcode,    prefix="/barcode",    tags=["Barcode"])
app.include_router(recipes,    prefix="/recipes",    tags=["Recipes"])
app.include_router(shopping,   prefix="/shopping",   tags=["Shopping"])
app.include_router(prediction, prefix="/prediction", tags=["Prediction"])
app.include_router(dashboard,  prefix="/dashboard",  tags=["Dashboard"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "version": "1.0.0"}
