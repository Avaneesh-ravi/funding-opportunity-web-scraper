from datetime import datetime
import pytz
from sqlalchemy.orm import Session

from app.models.website import Website
from app.models.opportunity import Opportunity, OpportunityHistory
from app.models.scrape_run import ScrapeRun
from app.scrapers.scraper_manager import scraper_manager
from app.scrapers.generic_scraper import ScraperNotConfiguredError
from app.scrapers.base import calculate_deadline_status
from app.services.activity_service import create_activity_log
from app.config import settings

def execute_website_scrape(db: Session, website_id: int, reference_now: datetime = None) -> ScrapeRun:
    """
    Executes a web scraping run for the given website ID.
    Tracks execution details in ScrapeRun and records history changes and in-website activity alerts.
    """
    website = db.query(Website).filter(Website.id == website_id).first()
    if not website:
        raise ValueError(f"Website with ID {website_id} not found.")

    tz = pytz.timezone(settings.TIMEZONE)
    now_utc = datetime.utcnow()
    
    scrape_run = ScrapeRun(
        website_id=website.id,
        started_at=now_utc,
        status="RUNNING"
    )
    db.add(scrape_run)
    db.commit()
    db.refresh(scrape_run)

    try:
        scraper = scraper_manager.get_scraper(
            target_url_or_type=website.target_url,
            scraper_type=website.scraper_type,
            website_id=website.id
        )
        
        # Scraper returns either a single ScrapedOpportunity or a List[ScrapedOpportunity]
        raw_result = scraper.scrape(website.target_url)
        if isinstance(raw_result, list):
            scraped_opps = raw_result
        elif raw_result is not None:
            scraped_opps = [raw_result]
        else:
            scraped_opps = []

        records_found = len(scraped_opps)
        records_created = 0
        records_updated = 0
        opp_id_for_log = None

        if records_found == 0:
            scrape_run.status = "SUCCESS"
            scrape_run.finished_at = datetime.utcnow()
            scrape_run.records_found = 0
            scrape_run.records_created = 0
            scrape_run.records_updated = 0
            scrape_run.error_message = "Scrape completed: No active funding opportunities detected on this page."
            db.commit()
            db.refresh(scrape_run)

            create_activity_log(
                db=db,
                event_type="SCRAPE_SUCCESS",
                title="Scraping Completed with No Opportunities",
                message=f"Scraped '{website.name}': Page processed successfully, but no active funding calls were identified.",
                website_id=website.id,
                dedup_key=f"run_empty_{scrape_run.id}"
            )
            return scrape_run

        for scraped_opp in scraped_opps:
            # Check if opportunity already exists in DB
            existing_opp = db.query(Opportunity).filter(
                Opportunity.website_id == website.id,
                (
                    (Opportunity.external_identifier.isnot(None) & (Opportunity.external_identifier == scraped_opp.external_identifier)) | 
                    (Opportunity.source_url == scraped_opp.source_url) |
                    (Opportunity.title == scraped_opp.title)
                )
            ).first()

            current_status = calculate_deadline_status(
                opening_date=scraped_opp.opening_date,
                current_deadline=scraped_opp.current_deadline,
                is_extended=scraped_opp.is_extended,
                verification_issue=scraped_opp.verification_issue,
                reference_now=reference_now,
                tz_name=settings.TIMEZONE
            )

            if existing_opp:
                # Audit field changes
                fields_to_track = [
                    ("current_deadline", scraped_opp.current_deadline),
                    ("title", scraped_opp.title),
                    ("document_url", scraped_opp.document_url),
                    ("description", scraped_opp.description),
                    ("eligibility", scraped_opp.eligibility)
                ]

                for field_name, new_val in fields_to_track:
                    old_val = getattr(existing_opp, field_name)
                    
                    # Format dates for clean comparison in history log
                    old_val_str = old_val.isoformat() if isinstance(old_val, datetime) else str(old_val or "")
                    new_val_str = new_val.isoformat() if isinstance(new_val, datetime) else str(new_val or "")

                    if old_val_str != new_val_str and new_val is not None:
                        history_entry = OpportunityHistory(
                            opportunity_id=existing_opp.id,
                            field_name=field_name,
                            old_value=old_val_str,
                            new_value=new_val_str,
                            changed_at=now_utc,
                            verification_source=scraped_opp.source_url
                        )
                        db.add(history_entry)

                        # Trigger In-Website Deadline Change notification
                        if field_name == "current_deadline":
                            create_activity_log(
                                db=db,
                                event_type="DEADLINE_CHANGED",
                                title="Submission Deadline Updated",
                                message=f"Deadline for '{existing_opp.title}' changed from {old_val_str} to {new_val_str}.",
                                website_id=website.id,
                                opportunity_id=existing_opp.id,
                                dedup_key=f"dl_change_{existing_opp.id}_{new_val_str}"
                            )

                # Update existing record
                existing_opp.title = scraped_opp.title
                existing_opp.scheme_name = scraped_opp.scheme_name or existing_opp.scheme_name
                existing_opp.funding_agency = scraped_opp.funding_agency or existing_opp.funding_agency
                existing_opp.description = scraped_opp.description or existing_opp.description
                existing_opp.announcement_date = scraped_opp.announcement_date or existing_opp.announcement_date
                existing_opp.opening_date = scraped_opp.opening_date or existing_opp.opening_date
                
                if not existing_opp.original_deadline and scraped_opp.original_deadline:
                    existing_opp.original_deadline = scraped_opp.original_deadline

                existing_opp.current_deadline = scraped_opp.current_deadline or existing_opp.current_deadline
                existing_opp.deadline_status = current_status
                existing_opp.funding_amount = scraped_opp.funding_amount or existing_opp.funding_amount
                existing_opp.eligibility = scraped_opp.eligibility or existing_opp.eligibility
                existing_opp.research_areas = scraped_opp.research_areas or existing_opp.research_areas
                existing_opp.project_duration = scraped_opp.project_duration or existing_opp.project_duration
                existing_opp.submission_instructions = scraped_opp.submission_instructions or existing_opp.submission_instructions
                existing_opp.application_url = scraped_opp.application_url or existing_opp.application_url
                existing_opp.document_url = scraped_opp.document_url or existing_opp.document_url
                existing_opp.source_url = scraped_opp.source_url
                existing_opp.last_seen_at = now_utc
                existing_opp.last_verified_at = now_utc
                existing_opp.updated_at = now_utc
                
                records_updated += 1
                opp_id_for_log = existing_opp.id
            else:
                # Create new opportunity record
                new_opp = Opportunity(
                    website_id=website.id,
                    external_identifier=scraped_opp.external_identifier,
                    title=scraped_opp.title,
                    scheme_name=scraped_opp.scheme_name,
                    funding_agency=scraped_opp.funding_agency,
                    description=scraped_opp.description,
                    announcement_date=scraped_opp.announcement_date,
                    opening_date=scraped_opp.opening_date,
                    original_deadline=scraped_opp.original_deadline,
                    current_deadline=scraped_opp.current_deadline,
                    deadline_status=current_status,
                    funding_amount=scraped_opp.funding_amount,
                    eligibility=scraped_opp.eligibility,
                    research_areas=scraped_opp.research_areas,
                    project_duration=scraped_opp.project_duration,
                    submission_instructions=scraped_opp.submission_instructions,
                    application_url=scraped_opp.application_url,
                    document_url=scraped_opp.document_url,
                    source_url=scraped_opp.source_url,
                    first_seen_at=now_utc,
                    last_seen_at=now_utc,
                    last_verified_at=now_utc,
                    created_at=now_utc,
                    updated_at=now_utc
                )
                db.add(new_opp)
                db.commit()
                db.refresh(new_opp)
                records_created += 1
                opp_id_for_log = new_opp.id

                # Trigger In-Website New Opportunity Alert
                create_activity_log(
                    db=db,
                    event_type="NEW_OPPORTUNITY",
                    title="New Funding Opportunity Discovered",
                    message=f"Discovered new call '{new_opp.title}' from {new_opp.funding_agency}.",
                    website_id=website.id,
                    opportunity_id=new_opp.id,
                    dedup_key=f"new_opp_{new_opp.id}"
                )

        scrape_run.status = "SUCCESS"
        scrape_run.finished_at = datetime.utcnow()
        scrape_run.records_found = records_found
        scrape_run.records_created = records_created
        scrape_run.records_updated = records_updated
        db.commit()
        db.refresh(scrape_run)

        # Trigger In-Website Scrape Success Activity Log
        create_activity_log(
            db=db,
            event_type="SCRAPE_SUCCESS",
            title="Scraping Completed Successfully",
            message=f"Scraped {website.name}: Found {records_found}, Created {records_created}, Updated {records_updated}.",
            website_id=website.id,
            opportunity_id=opp_id_for_log,
            dedup_key=f"run_success_{scrape_run.id}"
        )

        return scrape_run

    except ScraperNotConfiguredError as e:
        db.rollback()
        scrape_run.status = "FAILED"
        scrape_run.finished_at = datetime.utcnow()
        scrape_run.error_message = f"Scraper not configured for URL: {website.target_url}"
        db.commit()
        db.refresh(scrape_run)

        # Trigger In-Website Scraper Not Configured Activity Notification
        create_activity_log(
            db=db,
            event_type="CONFIG_REQUIRED",
            title="Scraper Configuration Required",
            message=f"Website '{website.name}' has no active scraper implementation configured.",
            website_id=website.id,
            dedup_key=f"config_req_{website.id}"
        )

        return scrape_run

    except Exception as e:
        db.rollback()
        scrape_run.status = "FAILED"
        scrape_run.finished_at = datetime.utcnow()
        scrape_run.error_message = f"Scraping failed: {str(e)}"
        db.commit()
        db.refresh(scrape_run)

        # Trigger In-Website Scrape Failed Notification
        create_activity_log(
            db=db,
            event_type="SCRAPE_FAILED",
            title="Scraping Run Failed",
            message=f"Scraping failed for '{website.name}': {str(e)}",
            website_id=website.id,
            dedup_key=f"run_failed_{scrape_run.id}"
        )

        return scrape_run
