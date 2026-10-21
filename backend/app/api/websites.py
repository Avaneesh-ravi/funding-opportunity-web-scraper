from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from urllib.parse import urlparse

from app.database import get_db
from app.models.website import Website
from app.schemas.website import WebsiteCreate, WebsiteUpdate, WebsiteResponse
from app.schemas.scrape_run import ScrapeRunResponse
from app.services.security_service import validate_url_security
from app.services.scraping_service import execute_website_scrape
from app.scrapers.scraper_manager import scraper_manager

router = APIRouter(prefix="/websites", tags=["Websites"])

@router.get("", response_model=List[WebsiteResponse])
def get_websites(db: Session = Depends(get_db)):
    """
    Get list of all configured websites.
    """
    websites = db.query(Website).order_by(Website.created_at.desc()).all()
    # Correct any legacy misnamed websites in database (e.g. DAE URL registered under AERB)
    for site in websites:
        if "dae.gov.in" in (site.target_url or "") and "AERB" in (site.name or ""):
            site.name = "Department of Atomic Energy (DAE)"
            site.category = "Public Consultation"
            db.commit()
    return websites


@router.post("", response_model=WebsiteResponse, status_code=status.HTTP_201_CREATED)
def create_website(website_in: WebsiteCreate, db: Session = Depends(get_db)):
    """
    Register a new website URL with SSRF security validation and trigger initial scrape.
    """
    # 1. SSRF and URL validation
    validate_url_security(website_in.target_url)
    
    # 2. Prevent duplicates
    existing = db.query(Website).filter(Website.target_url == website_in.target_url).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A website with this target URL is already registered."
        )

    # 3. Determine scraper type
    scraper_type = scraper_manager.get_scraper_type(website_in.target_url)

    parsed = urlparse(website_in.target_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    name = website_in.name
    category = website_in.category or "Research Grants"

    # Auto-detect real agency and category from content/domain
    try:
        from app.scrapers.universal_engine.opportunity_classifier import infer_funding_agency
        agency = infer_funding_agency(website_in.target_url)
        if agency and agency not in ("External Portal", "Funding Organization"):
            if not name or name == website_in.target_url or "generic" in name.lower() or "aerb" in name.lower():
                name = agency
        if "dae.gov.in" in website_in.target_url:
            name = "Department of Atomic Energy (DAE)"
            category = "Public Consultation"
        elif "aicte-india.org" in website_in.target_url:
            name = "All India Council for Technical Education (AICTE)"
            category = "Research Grants"
    except Exception:
        pass

    new_website = Website(
        name=name,
        base_url=website_in.base_url or base_url,
        target_url=website_in.target_url,
        category=category,
        description=website_in.description,
        scraper_type=scraper_type,
        enabled=website_in.enabled
    )
    db.add(new_website)
    db.commit()
    db.refresh(new_website)

    # 4. Automatically trigger initial scrape so records appear immediately
    try:
        execute_website_scrape(db, new_website.id)
        db.refresh(new_website)
    except Exception:
        pass

    return new_website


@router.get("/{website_id}", response_model=WebsiteResponse)
def get_website(website_id: int, db: Session = Depends(get_db)):
    website = db.query(Website).filter(Website.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found.")
    return website


@router.patch("/{website_id}", response_model=WebsiteResponse)
def update_website(website_id: int, website_in: WebsiteUpdate, db: Session = Depends(get_db)):
    website = db.query(Website).filter(Website.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found.")
    
    if website_in.target_url:
        validate_url_security(website_in.target_url)
        website.target_url = website_in.target_url
        website.scraper_type = scraper_manager.get_scraper_type(website_in.target_url)

    if website_in.name is not None:
        website.name = website_in.name
    if website_in.base_url is not None:
        website.base_url = website_in.base_url
    if website_in.category is not None:
        website.category = website_in.category
    if website_in.description is not None:
        website.description = website_in.description
    if website_in.enabled is not None:
        website.enabled = website_in.enabled

    db.commit()
    db.refresh(website)
    return website


@router.delete("/{website_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_website(website_id: int, db: Session = Depends(get_db)):
    website = db.query(Website).filter(Website.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found.")
    db.delete(website)
    db.commit()
    return None


@router.post("/{website_id}/scrape", response_model=ScrapeRunResponse)
def trigger_website_scrape(website_id: int, db: Session = Depends(get_db)):
    """
    Triggers an immediate web scrape for a specific registered website.
    """
    website = db.query(Website).filter(Website.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found.")

    scrape_run = execute_website_scrape(db, website_id)
    return scrape_run
