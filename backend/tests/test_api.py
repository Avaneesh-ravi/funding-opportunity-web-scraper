from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timezone" in data

def test_get_websites_contains_brns():
    response = client.get("/api/websites")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    brns_site = next((w for w in data if "brns.res.in" in w["target_url"]), None)
    assert brns_site is not None
    assert brns_site["scraper_type"] == "brns"

def test_add_url_ssrf_blocked():
    # Test localhost SSRF prevention
    payload = {
        "name": "Malicious Internal Target",
        "base_url": "http://127.0.0.1",
        "target_url": "http://127.0.0.1:8000/secret",
        "category": "Testing"
    }
    response = client.post("/api/websites", json=payload)
    assert response.status_code == 400
    assert "forbidden" in response.json()["detail"].lower() or "internal" in response.json()["detail"].lower()

def test_add_unsupported_url_and_scrape():
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    # Register unsupported website URL
    payload = {
        "name": f"Generic University Portal {unique_id}",
        "base_url": "https://example.com",
        "target_url": f"https://example.com/research-grants-{unique_id}",
        "category": "Generic Grants"
    }
    create_res = client.post("/api/websites", json=payload)
    assert create_res.status_code == 201
    site_id = create_res.json()["id"]

    # Trigger scrape for unsupported website
    scrape_res = client.post(f"/api/websites/{site_id}/scrape")
    assert scrape_res.status_code == 200
    scrape_data = scrape_res.json()
    assert scrape_data["status"] == "FAILED"
    assert "scraper not configured" in scrape_data["error_message"].lower()


def test_get_websites_contains_dst():
    response = client.get("/api/websites")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    dst_site = next((w for w in data if "onlinedst.gov.in" in w["target_url"] or w.get("scraper_type") == "dst"), None)
    assert dst_site is not None
    assert dst_site["scraper_type"] == "dst"
    assert "dst" in dst_site["target_url"].lower()


def test_scraper_manager_dst_variations():
    from app.scrapers.scraper_manager import scraper_manager
    from app.scrapers.dst_scraper import DSTScraper

    # Various DST URL representations & keys
    variations = [
        "https://onlinedst.gov.in/Projectproposalformat.aspx?Id=2232",
        "http://onlinedst.gov.in/Projectproposalformat.aspx?Id=2232",
        "https://ONLINEDST.GOV.IN/Projectproposalformat.aspx?Id=2232",
        "https://dst.gov.in/whats-new",
        "http://dst.gov.in/",
        "onlinedst.gov.in",
        "dst.gov.in",
        "dst",
        "dst_scraper",
        2,  # Seeded website ID
        "2",
    ]

    for var in variations:
        assert scraper_manager.get_scraper_type(var) == "dst", f"Failed for {var}"
        scraper = scraper_manager.get_scraper(var)
        assert isinstance(scraper, DSTScraper), f"Failed scraper instance for {var}"


def test_scraper_manager_brns_variations():
    from app.scrapers.scraper_manager import scraper_manager
    from app.scrapers.brns_scraper import BRNSScraper

    variations = [
        "https://brns.res.in/content_details.php?content_id=69",
        "http://BRNS.RES.IN/index.php",
        "brns.res.in",
        "brns",
        "brns_scraper",
        1,  # Seeded website ID
        "1",
    ]

    for var in variations:
        assert scraper_manager.get_scraper_type(var) == "brns", f"Failed for {var}"
        scraper = scraper_manager.get_scraper(var)
        assert isinstance(scraper, BRNSScraper), f"Failed scraper instance for {var}"


def test_scraper_manager_unsupported_urls():
    from app.scrapers.scraper_manager import scraper_manager
    from app.scrapers.generic_scraper import GenericScraper

    # URLs that contain "dst" as a substring in words but are NOT DST domains
    tricky_urls = [
        "https://example.com/research-grants",
        "https://university.edu/podcast-series",
        "https://industry.gov.in/funds",
        "https://example.com/dst-fake",
    ]

    for url in tricky_urls:
        assert scraper_manager.get_scraper_type(url) == "generic", f"Should be generic for {url}"
        scraper = scraper_manager.get_scraper(url)
        assert isinstance(scraper, GenericScraper), f"Should return GenericScraper for {url}"


def test_create_website_without_base_url():
    import uuid
    uid = str(uuid.uuid4())[:8]
    payload = {
        "name": f"Portal Without Base URL {uid}",
        "target_url": f"https://example.org/portal-{uid}",
        "category": "Fellowships"
    }
    res = client.post("/api/websites", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["base_url"] == "https://example.org"
    assert data["target_url"] == f"https://example.org/portal-{uid}"
