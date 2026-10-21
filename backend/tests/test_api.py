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
