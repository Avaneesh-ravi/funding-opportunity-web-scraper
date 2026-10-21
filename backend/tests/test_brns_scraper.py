from datetime import datetime
from bs4 import BeautifulSoup
from app.scrapers.brns_scraper import BRNSScraper

SAMPLE_BRNS_HTML = """
<html>
<body>
<td class="content">
<p><font size='4'>Call for Coordinated Research Projects (CRPs)-2026</font><br><hr><br/>
<h2><span><span>Call for Coordinated Research Projects (CRPs)-2026 Phase-I</span></span></h2>
<h3><span><span><strong>Announced on : May 20, 2026</strong></span></span></h3>
<h3><span><span><strong>Last Date of submission:&nbsp;</strong></span></span><span><span><strong>August 31, 2026</strong></span></span></h3>
<a href="https://brns.res.in/public_files/BRNS_Announcement_for_CRP-2026_Phase1.pdf"><span><span>Detail Document</span></span></a>
</h3>
</td>
</body>
</html>
"""

def test_brns_html_extraction_fixture():
    scraper = BRNSScraper()
    soup = BeautifulSoup(SAMPLE_BRNS_HTML, "html.parser")
    page_text = soup.get_text(" ", strip=True).replace('\xa0', ' ')

    ann_date = scraper._parse_date_regex(r"Announced\s+on\s*:\s*([A-Za-z]+\s+\d{1,2},\s*\d{4})", page_text)
    deadline_date = scraper._parse_date_regex(r"Last\s+Date\s+of\s+submission\s*:\s*([A-Za-z]+\s+\d{1,2},\s*\d{4})", page_text)

    assert ann_date is not None
    assert ann_date.year == 2026
    assert ann_date.month == 5
    assert ann_date.day == 20

    assert deadline_date is not None
    assert deadline_date.year == 2026
    assert deadline_date.month == 8
    assert deadline_date.day == 31

def test_brns_detail_document_url_resolution():
    soup = BeautifulSoup(SAMPLE_BRNS_HTML, "html.parser")
    doc_url = None
    target_url = "https://brns.res.in/content_details.php?content_id=69"
    for a_tag in soup.find_all("a", href=True):
        if "detail document" in a_tag.get_text().lower():
            doc_url = a_tag["href"]
            break
    assert doc_url == "https://brns.res.in/public_files/BRNS_Announcement_for_CRP-2026_Phase1.pdf"
