import io
import json
from datetime import datetime
import pytest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup

from app.scrapers.universal_engine.universal_scraper import UniversalScraper
from app.scrapers.universal_engine.http_client import SafeHttpClient, SafeResponse
from app.scrapers.universal_engine.date_utils import parse_flexible_date, extract_dates_from_text
from app.scrapers.universal_engine.metadata_extractor import extract_html_metadata, parse_feed_content
from app.scrapers.universal_engine.opportunity_classifier import (
    calculate_opportunity_confidence,
    infer_funding_agency,
    extract_opportunities_from_table
)
from app.scrapers.universal_engine.browser_fallback import is_spa_shell
from app.services.security_service import validate_url_security
from fastapi import HTTPException


# ── 1. Test New Unconfigured Domain Extraction ─────────────────────────────────

def test_new_unconfigured_domain_extraction():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Call for Research Proposals in Clean Energy 2026 - IIT Delhi</title>
        <meta name="description" content="Inviting competitive research project proposals in clean energy technologies.">
    </head>
    <body>
        <h1>Call for Research Proposals in Clean Energy 2026</h1>
        <p>The Energy Research Initiative invites faculty members to submit research proposals.</p>
        <div class="dates">
            <p>Announced on: 15 October 2026</p>
            <p>Last Date of submission: 30 November 2026</p>
        </div>
        <p>Eligibility: Full-time faculty members and researchers from recognized Indian universities.</p>
        <p>Grant funding amount: Up to Rs. 45 Lakhs per project.</p>
        <a href="/docs/clean_energy_call_guidelines.pdf">Download Proposal Guidelines (PDF)</a>
    </body>
    </html>
    """
    scraper = UniversalScraper()
    mock_response = SafeResponse(
        url="https://iitd.ac.in/research/clean-energy-call",
        status_code=200,
        content=html_content.encode("utf-8"),
        headers={"content-type": "text/html; charset=utf-8"}
    )

    with patch.object(scraper.http_client, "fetch", return_value=mock_response):
        opps = scraper.scrape_all("https://iitd.ac.in/research/clean-energy-call")

    assert len(opps) == 1
    opp = opps[0]
    assert "Clean Energy 2026" in opp.title
    assert opp.funding_agency == "IITD"
    assert opp.announcement_date is not None
    assert opp.announcement_date.year == 2026
    assert opp.announcement_date.month == 10
    assert opp.current_deadline is not None
    assert opp.current_deadline.year == 2026
    assert opp.current_deadline.month == 11
    assert opp.deadline_status in ("Open", "Closing Soon", "Upcoming")
    assert opp.document_url == "https://iitd.ac.in/docs/clean_energy_call_guidelines.pdf"


# ── 2. Test Listing Page Linking to Multiple Detail Pages / Table ──────────────

def test_listing_page_with_multiple_opportunities():
    html_content = """
    <html>
    <head><title>Ongoing Grants & Calls - Research Foundation</title></head>
    <body>
        <h2>Active Calls for Proposals</h2>
        <table id="calls-table">
            <thead>
                <tr>
                    <th>S.No</th>
                    <th>Call Title / Scheme</th>
                    <th>Start Date</th>
                    <th>Closing Date</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>National Quantum Mission Call for Collaborative Projects 2026</td>
                    <td>01/09/2026</td>
                    <td>15/12/2026</td>
                    <td><a href="/files/quantum_call.pdf">View PDF</a></td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>AI for Healthcare Research Initiative Fellowship 2026</td>
                    <td>15/09/2026</td>
                    <td>31/10/2026</td>
                    <td><a href="/files/ai_health.pdf">Guidelines PDF</a></td>
                </tr>
            </tbody>
        </table>
    </body>
    </html>
    """
    scraper = UniversalScraper()
    mock_res = SafeResponse(
        url="https://foundation.org/calls",
        status_code=200,
        content=html_content.encode("utf-8"),
        headers={"content-type": "text/html"}
    )

    with patch.object(scraper.http_client, "fetch", return_value=mock_res):
        opps = scraper.scrape_all("https://foundation.org/calls")

    assert len(opps) == 2
    titles = [o.title for o in opps]
    assert any("Quantum Mission" in t for t in titles)
    assert any("AI for Healthcare" in t for t in titles)


# ── 3. Test Site Containing Structured Metadata (JSON-LD) ──────────────────────

def test_site_with_json_ld_metadata():
    json_ld = {
        "@context": "https://schema.org",
        "@type": "Grant",
        "name": "Global Climate Resilience Research Grant 2026",
        "description": "Funding for innovative climate adaptation and resilience projects.",
        "startDate": "2026-08-01",
        "validThrough": "2026-11-20",
        "funder": {"@type": "Organization", "name": "Global Climate Alliance"}
    }
    html_content = f"""
    <html>
    <head>
        <title>Climate Grant</title>
        <script type="application/ld+json">{json.dumps(json_ld)}</script>
    </head>
    <body>
        <h1>Global Climate Resilience Research Grant 2026</h1>
        <p>Application details for international research collaborations.</p>
    </body>
    </html>
    """
    scraper = UniversalScraper()
    mock_res = SafeResponse(
        url="https://climatealliance.org/grants/2026",
        status_code=200,
        content=html_content.encode("utf-8"),
        headers={"content-type": "text/html"}
    )

    with patch.object(scraper.http_client, "fetch", return_value=mock_res):
        opps = scraper.scrape_all("https://climatealliance.org/grants/2026")

    assert len(opps) >= 1
    opp = opps[0]
    assert "Global Climate Resilience" in opp.title
    assert opp.funding_agency == "Global Climate Alliance"
    assert opp.current_deadline is not None
    assert opp.current_deadline.year == 2026


# ── 4. Test Page With No Deadline (Never Invent Missing Information) ───────────

def test_page_with_no_deadline_keeps_null():
    html_content = """
    <html>
    <head><title>Open-Ended Research Grants</title></head>
    <body>
        <h1>Call for Proposals in Theoretical Physics</h1>
        <p>Proposals are accepted on a rolling basis throughout the year. There is no submission deadline.</p>
        <p>Announced on: 10 January 2026</p>
    </body>
    </html>
    """
    scraper = UniversalScraper()
    mock_res = SafeResponse(
        url="https://physics-inst.org/open-call",
        status_code=200,
        content=html_content.encode("utf-8"),
        headers={"content-type": "text/html"}
    )

    with patch.object(scraper.http_client, "fetch", return_value=mock_res):
        opps = scraper.scrape_all("https://physics-inst.org/open-call")

    assert len(opps) == 1
    opp = opps[0]
    assert opp.current_deadline is None
    assert opp.deadline_status == "Unknown"


# ── 5. Test Page With No Funding Opportunities (No False Positives) ────────────

def test_page_containing_no_funding_opportunities():
    html_content = """
    <html>
    <head><title>About Our Organization - Team & History</title></head>
    <body>
        <h1>About Our Organization</h1>
        <p>We are a non-profit technology organization founded in 2015.</p>
        <p>Our team works on software development, infrastructure, and design.</p>
        <p>Contact us at info@example.com for partnership inquiries.</p>
    </body>
    </html>
    """
    scraper = UniversalScraper()
    mock_res = SafeResponse(
        url="https://tech-company.org/about",
        status_code=200,
        content=html_content.encode("utf-8"),
        headers={"content-type": "text/html"}
    )

    with patch.object(scraper.http_client, "fetch", return_value=mock_res):
        opps = scraper.scrape_all("https://tech-company.org/about")

    assert len(opps) == 0


# ── 6. Test JavaScript-Rendered SPA Shell Detection ────────────────────────────

def test_spa_shell_detection():
    spa_html = '<html><head><title>React App</title></head><body><div id="root"></div><script src="/bundle.js"></script></body></html>'
    assert is_spa_shell(spa_html, body_text_len=10) is True

    static_html = '<html><head><title>Page</title></head><body><h1>Content</h1>' + ('<p>Lots of content text here.</p>' * 30) + '</body></html>'
    assert is_spa_shell(static_html, body_text_len=600) is False


# ── 7. Test RSS Feed Extraction ────────────────────────────────────────────────

def test_rss_feed_extraction():
    rss_content = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>National Science Grants Feed</title>
            <link>https://sciencegrants.gov/rss</link>
            <item>
                <title>Call for Research Proposals in Semiconductor Packaging 2026</title>
                <link>https://sciencegrants.gov/calls/semi-2026</link>
                <description>Funding opportunity for advanced packaging research projects.</description>
                <pubDate>Mon, 05 Oct 2026 10:00:00 GMT</pubDate>
            </item>
        </channel>
    </rss>
    """
    scraper = UniversalScraper()
    mock_res = SafeResponse(
        url="https://sciencegrants.gov/feed.xml",
        status_code=200,
        content=rss_content.encode("utf-8"),
        headers={"content-type": "application/rss+xml"}
    )

    with patch.object(scraper.http_client, "fetch", return_value=mock_res):
        opps = scraper.scrape_all("https://sciencegrants.gov/feed.xml")

    assert len(opps) >= 1
    assert "Semiconductor Packaging" in opps[0].title


# ── 8. Test SSRF Protection on Fetching and Redirects ──────────────────────────

def test_ssrf_protection():
    # Loopback IP
    with pytest.raises(HTTPException) as exc1:
        validate_url_security("http://127.0.0.1:8000/admin")
    assert exc1.value.status_code == 400

    # Localhost string
    with pytest.raises(HTTPException) as exc2:
        validate_url_security("http://localhost/secret")
    assert exc2.value.status_code == 400

    # AWS/GCP metadata endpoint
    with pytest.raises(HTTPException) as exc3:
        validate_url_security("http://169.254.169.254/latest/meta-data")
    assert exc3.value.status_code == 400

    # Private network
    with pytest.raises(HTTPException) as exc4:
        validate_url_security("http://10.0.0.5:5432")
    assert exc4.value.status_code == 400


# ── 9. Test Flexible Date Parser ───────────────────────────────────────────────

def test_flexible_date_parsing():
    d1 = parse_flexible_date("31/10/2026")
    assert d1 is not None and d1.day == 31 and d1.month == 10 and d1.year == 2026

    d2 = parse_flexible_date("15th November 2026")
    assert d2 is not None and d2.day == 15 and d2.month == 11 and d2.year == 2026

    d3 = parse_flexible_date("2026-12-25")
    assert d3 is not None and d3.day == 25 and d3.month == 12 and d3.year == 2026

    ann, dl = extract_dates_from_text("Announced on: 01-Oct-2026. Last Date of submission: 15-Nov-2026 upto 5:00 PM.")
    assert ann is not None and ann.day == 1 and ann.month == 10
    assert dl is not None and dl.day == 15 and dl.month == 11
