import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models.website import Website
from app.api.websites import router as websites_router
from app.api.opportunities import router as opportunities_router
from app.api.scrape_runs import router as scrape_runs_router
from app.api.activities import router as activities_router
from app.services.scheduler_service import scraping_scheduler

logger = logging.getLogger(__name__)

# ── Create tables ─────────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)


# ── Application lifespan ──────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Startup: creating DB tables and seeding default websites...")
    seed_default_websites()
    logger.info("Startup: starting scraping scheduler (24 h interval)...")
    scraping_scheduler.start(interval_hours=24)
    logger.info("Startup complete. CORS origins: %s", settings.CORS_ORIGINS)
    yield
    logger.info("Shutdown: stopping scheduler...")
    scraping_scheduler.shutdown()


# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Automated Web Scraping Dashboard and Funding Opportunity Tracker "
        "for BRNS and DST research grant portals."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — origins sourced from CORS_ORIGINS_STR env var; no wildcard in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(websites_router, prefix="/api")
app.include_router(opportunities_router, prefix="/api")
app.include_router(scrape_runs_router, prefix="/api")
app.include_router(activities_router, prefix="/api")


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.PROJECT_NAME,
        "timezone": settings.TIMEZONE,
        "debug": settings.DEBUG,
        "scheduler_running": scraping_scheduler.scheduler.running,
        "cors_origins": settings.CORS_ORIGINS,
    }


# ── Seed helper ───────────────────────────────────────────────────────────────
def seed_default_websites():
    db = SessionLocal()
    try:
        _seed_if_missing(
            db,
            target_url="https://brns.res.in/content_details.php?content_id=69",
            name="Board of Research in Nuclear Sciences (BRNS)",
            base_url="https://brns.res.in",
            category="Nuclear Research Grants",
            description=(
                "Official BRNS portal for research project calls "
                "and fellowship funding opportunities."
            ),
            scraper_type="brns",
        )
        _seed_if_missing(
            db,
            target_url="https://onlinedst.gov.in/Projectproposalformat.aspx?Id=2232",
            name="Department of Science and Technology (DST)",
            base_url="https://onlinedst.gov.in",
            category="Science & Technology Grants",
            description=(
                "Official DST e-PMS portal for project proposals "
                "and international scientific training groups."
            ),
            scraper_type="dst",
        )
        db.commit()
    except Exception as exc:
        logger.error("Error seeding default websites: %s", exc)
    finally:
        db.close()


def _seed_if_missing(db, *, target_url, name, base_url, category, description, scraper_type):
    exists = db.query(Website).filter(Website.target_url == target_url).first()
    if exists:
        if exists.scraper_type != scraper_type:
            exists.scraper_type = scraper_type
            logger.info("Updated scraper_type to %s for website: %s", scraper_type, name)
    else:
        db.add(Website(
            name=name,
            base_url=base_url,
            target_url=target_url,
            category=category,
            description=description,
            scraper_type=scraper_type,
            enabled=True,
        ))
        logger.info("Seeded website: %s", name)


# ── Local development entry point ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
