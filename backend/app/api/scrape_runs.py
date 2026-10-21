from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.scrape_run import ScrapeRun
from app.schemas.scrape_run import ScrapeRunResponse

router = APIRouter(prefix="/scrape-runs", tags=["Scrape History"])

@router.get("", response_model=List[ScrapeRunResponse])
def get_scrape_runs(limit: int = 50, db: Session = Depends(get_db)):
    """
    Get scraping history logs sorted by most recent first.
    Auto-heals any orphaned runs stuck in RUNNING state due to server crashes or timeouts.
    """
    now_utc = datetime.utcnow()
    stale_cutoff = now_utc - timedelta(minutes=2)
    stale_runs = db.query(ScrapeRun).filter(
        ScrapeRun.status == "RUNNING",
        ScrapeRun.started_at < stale_cutoff
    ).all()
    if stale_runs:
        for s in stale_runs:
            s.status = "FAILED"
            s.finished_at = now_utc
            s.error_message = "Scrape run timed out or was terminated."
        db.commit()

    return db.query(ScrapeRun).order_by(ScrapeRun.started_at.desc()).limit(limit).all()
