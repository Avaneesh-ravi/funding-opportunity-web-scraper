from app.database import SessionLocal, Base, engine
from app.models.website import Website
from app.services.scraping_service import execute_website_scrape
from app.models.opportunity import Opportunity

def run_dst_live_test():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        dst_url = "https://onlinedst.gov.in/Projectproposalformat.aspx?Id=2232"
        website = db.query(Website).filter(Website.target_url == dst_url).first()
        if not website:
            website = Website(
                name="Department of Science and Technology (DST)",
                base_url="https://onlinedst.gov.in",
                target_url=dst_url,
                category="Science & Technology Grants",
                description="DST e-PMS portal for project proposals and international scientific training groups.",
                scraper_type="dst",
                enabled=True
            )
            db.add(website)
            db.commit()
            db.refresh(website)

        print(f"Triggering live scrape for DST website ID {website.id}...")
        scrape_run = execute_website_scrape(db, website.id)
        
        print("\n=== DST SCRAPE RUN RESULT ===")
        print(f"Status: {scrape_run.status}")
        print(f"Records Found: {scrape_run.records_found}")
        print(f"Records Created: {scrape_run.records_created}")
        print(f"Records Updated: {scrape_run.records_updated}")
        print(f"Error Message: {scrape_run.error_message}")

        opp = db.query(Opportunity).filter(Opportunity.website_id == website.id).first()
        if opp:
            print("\n=== EXTRACTED DST OPPORTUNITY DETAILS ===")
            print(f"Title: {opp.title}")
            print(f"Funding Agency: {opp.funding_agency}")
            print(f"Scheme Name: {opp.scheme_name}")
            print(f"Deadline Status: {opp.deadline_status}")
            print(f"Detail Document URL: {opp.document_url}")
            print(f"Application Portal URL: {opp.application_url}")
            print(f"Source URL: {opp.source_url}")
            print(f"Description: {opp.description[:150]}...")
            print(f"Last Verified At: {opp.last_verified_at}")

    finally:
        db.close()

if __name__ == "__main__":
    run_dst_live_test()
