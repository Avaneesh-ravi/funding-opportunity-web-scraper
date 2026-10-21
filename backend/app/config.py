import os
import logging
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "Web Scraping Dashboard — BRNS Funding Opportunity Tracker"

    # Set to False in production via env var: DEBUG=false
    DEBUG: bool = False

    # SQLite default (local dev). On Render override with the persistent disk path:
    #   DATABASE_URL=sqlite:////opt/render/project/data/dashboard.db
    DATABASE_URL: str = "sqlite:///./data/dashboard.db"

    # Comma-separated list of allowed CORS origins — no wildcard in production.
    # On Render set:  CORS_ORIGINS_STR=https://your-app.vercel.app
    CORS_ORIGINS_STR: str = "http://localhost:5173,http://127.0.0.1:5173"

    TIMEZONE: str = "Asia/Kolkata"

    # HTTP timeout for scraper outbound requests (seconds)
    SCRAPER_TIMEOUT: int = 30

    DEFAULT_USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    @property
    def CORS_ORIGINS(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS_STR.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
