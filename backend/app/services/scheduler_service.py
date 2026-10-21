import logging
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models.website import Website
from app.services.scraping_service import execute_website_scrape

logger = logging.getLogger(__name__)


class ScrapingScheduler:
    """
    Wraps APScheduler BackgroundScheduler for daily scraping.

    Important production note
    ─────────────────────────
    Render's free tier runs a **single process** (1 worker), so APScheduler
    running inside the web process is fine and will not produce duplicate jobs.
    If you ever scale to multiple Uvicorn workers (--workers N > 1), move the
    scheduler to a dedicated Render Background Worker service that runs:
        python -m app.worker
    and set DISABLE_SCHEDULER=true on all web-worker instances.
    """

    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone=settings.TIMEZONE)

    def start(self, interval_hours: int = 24):
        """Start the scheduler if not already running."""
        if self.scheduler.running:
            logger.warning("Scheduler already running — skipping duplicate start.")
            return

        # Use a CronTrigger at midnight Asia/Kolkata instead of a plain interval
        # so the job fires at a predictable wall-clock time regardless of startup time.
        self.scheduler.add_job(
            func=self.run_scheduled_scrapes,
            trigger=CronTrigger(hour=0, minute=0, timezone=settings.TIMEZONE),
            id="daily_scrape_job",
            replace_existing=True,          # safe even if called more than once
            name="Daily Automatic Funding Opportunity Scraping Job",
            misfire_grace_time=3600,        # tolerate up to 1 h startup delay
        )
        self.scheduler.start()
        logger.info(
            "Scraping scheduler started — daily job at 00:00 %s.", settings.TIMEZONE
        )

    def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Scraping scheduler stopped.")

    def run_scheduled_scrapes(self):
        """Scrape all enabled websites. Called by the scheduler."""
        logger.info("Scheduled scrape: starting run for all enabled portals...")
        db: Session = SessionLocal()
        try:
            websites = db.query(Website).filter(Website.enabled == True).all()
            logger.info("Scheduled scrape: found %d enabled portal(s).", len(websites))
            for website in websites:
                try:
                    execute_website_scrape(db, website.id)
                    logger.info("Scheduled scrape: completed for '%s'.", website.name)
                except Exception as exc:
                    logger.error(
                        "Scheduled scrape: failed for website id=%s (%s): %s",
                        website.id, website.name, exc,
                    )
        finally:
            db.close()


# Module-level singleton — imported by main.py
scraping_scheduler = ScrapingScheduler()
