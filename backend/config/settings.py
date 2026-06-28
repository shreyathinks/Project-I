from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ── Database ──────────────────────────────────────────────────────────────
    database_url: str = "postgresql://kitchen_user:kitchen_pass@localhost:5432/kitchen_db"

    # ── Security ──────────────────────────────────────────────────────────────
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # ── Redis ─────────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── Ollama ────────────────────────────────────────────────────────────────
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # ── Email ─────────────────────────────────────────────────────────────────
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = ""
    notifications_enabled: bool = True

    # ── OCR ───────────────────────────────────────────────────────────────────
    ocr_engine: str = "paddle"  # paddle | tesseract

    # ── App ───────────────────────────────────────────────────────────────────
    app_env: str = "development"
    debug: bool = True

    # ── CORS ─────────────────────────────────────────────────────────────────
    @property
    def cors_origins(self) -> List[str]:
        return [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:80",
            "http://localhost",
        ]

    # ── ML paths ─────────────────────────────────────────────────────────────
    models_cache_dir: str = "models_cache"
    datasets_dir: str = "datasets"


settings = Settings()
