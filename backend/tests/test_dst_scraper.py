from datetime import datetime
from bs4 import BeautifulSoup
from app.scrapers.dst_scraper import DSTScraper
from app.database import SessionLocal
from app.models.website import Website
from app.models.opportunity import Opportunity
from app.services.scraping_service import execute_website_scrape

SAMPLE_DST_HTML = """
<html>
<body>
<div id="aspnetForm">
  <table class="table table-bordered table-hover">
    <tr style="background-color:#4b6d84;">
      <td><span>International Cooperation Division</span></td>
    </tr>
    <tr>
      <td>1.</td>
      <td>
        <a href="Projectproposalformat.aspx?Id=2232">DST DFG joint call on International Research Training Groups (IRTG)</a>
      </td>
      <td>
        <span><b>(Active)</b><br>(Throughout the Year) (IST)</span>
      </td>
      <td>
        <a href="Documents\\ProjectProposalFormat\\SchemeId_2232_DFG_IRTGCallGuidelines.pdf">Download</a>
      </td>
    </tr>
  </table>
  <div id="des2232">
    <p>International Research Training Groups IRTGs combine innovative top-level research and structured promotion of early career researchers.</p>
  </div>
</div>
</body>
</html>
"""

def test_dst_html_extraction_fixture():
    scraper = DSTScraper()
    soup = BeautifulSoup(SAMPLE_DST_HTML, "html.parser")
    title_a = soup.find("a", href=True)
    assert title_a is not None
    assert title_a.get_text(strip=True) == "DST DFG joint call on International Research Training Groups (IRTG)"

def test_dst_duplicate_detection_and_scrape():
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
                description="DST e-PMS portal for international research training groups.",
                scraper_type="dst",
                enabled=True
            )
            db.add(website)
            db.commit()
            db.refresh(website)

        # Scrape run 1: Creation
        run1 = execute_website_scrape(db, website.id)
        assert run1.status == "SUCCESS"
        assert run1.records_created == 1 or run1.records_updated == 1

        # Scrape run 2: Duplicate check -> should update rather than duplicate
        count_before = db.query(Opportunity).filter(Opportunity.website_id == website.id).count()
        run2 = execute_website_scrape(db, website.id)
        assert run2.status == "SUCCESS"
        count_after = db.query(Opportunity).filter(Opportunity.website_id == website.id).count()
        
        assert count_before == count_after
    finally:
        db.close()
