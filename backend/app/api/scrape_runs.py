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
    """
    return db.query(ScrapeRun).order_by(ScrapeRun.started_at.desc()).limit(limit).all()
