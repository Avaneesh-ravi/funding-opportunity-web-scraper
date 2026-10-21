from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc

from app.database import get_db
from app.models.opportunity import Opportunity
from app.schemas.opportunity import OpportunityResponse
from app.schemas.scrape_run import ScrapeRunResponse
from app.services.scraping_service import execute_website_scrape
from app.services.export_service import export_opportunities_to_csv, export_opportunities_to_excel
from app.scrapers.base import calculate_deadline_status
from app.config import settings

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])

@router.get("", response_model=List[OpportunityResponse])
def get_opportunities(
    q: Optional[str] = Query(None, description="Search term for title, agency, or scheme"),
    status: Optional[str] = Query(None, description="Filter by status: Open, Closing Soon, Closed, Upcoming, Extended, Unknown"),
    website_id: Optional[int] = Query(None, description="Filter by website ID"),
    sort_by: Optional[str] = Query("deadline_asc", description="Sort by: deadline_asc, deadline_desc, date_desc, updated_desc"),
    db: Session = Depends(get_db)
):
    """
    Get funding opportunities with search, filtering, and sorting options.
    Re-calculates deadline status dynamically based on current date.
    """
    query = db.query(Opportunity)

    if website_id:
        query = query.filter(Opportunity.website_id == website_id)

    if q:
        search_pattern = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Opportunity.title.ilike(search_pattern),
                Opportunity.funding_agency.ilike(search_pattern),
                Opportunity.scheme_name.ilike(search_pattern),
                Opportunity.description.ilike(search_pattern)
            )
        )

    opportunities = query.all()

    # Recalculate deadline status against current datetime
    for opp in opportunities:
        new_status = calculate_deadline_status(
            opening_date=opp.opening_date,
            current_deadline=opp.current_deadline,
            tz_name=settings.TIMEZONE
        )
        if opp.deadline_status != new_status and opp.deadline_status not in ("Verification Required", "Extended"):
            opp.deadline_status = new_status
    db.commit()

    # Apply status filter after dynamic calculation
    if status:
        opportunities = [o for o in opportunities if o.deadline_status.lower() == status.lower()]

    # Apply sorting
    if sort_by == "deadline_asc":
        opportunities.sort(key=lambda x: (x.current_deadline is None, x.current_deadline or datetime.max))
    elif sort_by == "deadline_desc":
        opportunities.sort(key=lambda x: (x.current_deadline is None, x.current_deadline or datetime.min), reverse=True)
    elif sort_by == "date_desc":
        opportunities.sort(key=lambda x: (x.announcement_date is None, x.announcement_date or datetime.min), reverse=True)
    elif sort_by == "updated_desc":
        opportunities.sort(key=lambda x: x.updated_at or datetime.min, reverse=True)

    return opportunities


@router.get("/export")
def export_opportunities(
    format: str = Query("csv", description="Format: csv or excel"),
    db: Session = Depends(get_db)
):
    """
    Export current opportunity records to CSV or Excel format.
    """
    opportunities = db.query(Opportunity).all()
    
    if format.lower() in ("excel", "xlsx"):
        stream = export_opportunities_to_excel(opportunities)
        filename = f"funding_opportunities_{datetime.utcnow().strftime('%Y%m%d')}.xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        stream = export_opportunities_to_csv(opportunities)
        filename = f"funding_opportunities_{datetime.utcnow().strftime('%Y%m%d')}.csv"
        media_type = "text/csv"

    headers = {
        "Content-Disposition": f"attachment; filename={filename}"
    }
    return StreamingResponse(stream, media_type=media_type, headers=headers)


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
def get_opportunity(opportunity_id: int, db: Session = Depends(get_db)):
    opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found.")
    
    # Recalculate status
    opp.deadline_status = calculate_deadline_status(
        opening_date=opp.opening_date,
        current_deadline=opp.current_deadline,
        tz_name=settings.TIMEZONE
    )
    db.commit()
    db.refresh(opp)
    return opp


@router.post("/{opportunity_id}/refresh", response_model=ScrapeRunResponse)
def refresh_opportunity(opportunity_id: int, db: Session = Depends(get_db)):
    """
    Re-scrapes the source website associated with this opportunity.
    """
    opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found.")

    scrape_run = execute_website_scrape(db, opp.website_id)
    return scrape_run
