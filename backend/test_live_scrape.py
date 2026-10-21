from app.database import SessionLocal, Base, engine
from app.models.website import Website
from app.services.scraping_service import execute_website_scrape
from app.models.opportunity import Opportunity

def run_live_test():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        brns_url = "https://brns.res.in/content_details.php?content_id=69"
        website = db.query(Website).filter(Website.target_url == brns_url).first()
        if not website:
            website = Website(
                name="Board of Research in Nuclear Sciences (BRNS)",
                base_url="https://brns.res.in",
                target_url=brns_url,
                category="Nuclear Research Grants",
                description="Official BRNS portal for research project calls and fellowship funding opportunities.",
                scraper_type="brns",
                enabled=True
            )
            db.add(website)
            db.commit()
            db.refresh(website)

        print(f"Triggering live scrape for website ID {website.id}...")
        scrape_run = execute_website_scrape(db, website.id)
        
        print("\n=== SCRAPE RUN RESULT ===")
        print(f"Status: {scrape_run.status}")
        print(f"Records Found: {scrape_run.records_found}")
        print(f"Records Created: {scrape_run.records_created}")
        print(f"Records Updated: {scrape_run.records_updated}")
        print(f"Error Message: {scrape_run.error_message}")

        opportunity = db.query(Opportunity).filter(Opportunity.website_id == website.id).first()
        if opportunity:
            print("\n=== EXTRACTED OPPORTUNITY DETAILS ===")
            print(f"Title: {opportunity.title}")
            print(f"Funding Agency: {opportunity.funding_agency}")
            print(f"Scheme Name: {opportunity.scheme_name}")
            print(f"Announcement Date: {opportunity.announcement_date}")
            print(f"Current Deadline: {opportunity.current_deadline}")
            print(f"Original Deadline: {opportunity.original_deadline}")
            print(f"Deadline Status: {opportunity.deadline_status}")
            print(f"Detail Document URL: {opportunity.document_url}")
            print(f"Application Portal URL: {opportunity.application_url}")
            print(f"Source URL: {opportunity.source_url}")
            print(f"Eligibility snippet: {opportunity.eligibility[:100]}...")
            print(f"Research Areas snippet: {opportunity.research_areas[:100]}...")
            print(f"Last Verified At: {opportunity.last_verified_at}")

    finally:
        db.close()

if __name__ == "__main__":
    run_live_test()
