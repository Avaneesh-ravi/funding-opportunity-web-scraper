from fastapi.testclient import TestClient
from app.main import app
from app.services.scheduler_service import scraping_scheduler
from app.services.activity_service import create_activity_log
from app.database import SessionLocal

client = TestClient(app)

def test_activity_deduplication():
    db = SessionLocal()
    try:
        # First creation
        act1 = create_activity_log(
            db=db,
            event_type="NEW_OPPORTUNITY",
            title="Test Event Title",
            message="Test Event Message",
            dedup_key="unique_test_123"
        )
        assert act1 is not None

        # Duplicate creation with same dedup_key -> should return existing record
        act2 = create_activity_log(
            db=db,
            event_type="NEW_OPPORTUNITY",
            title="Test Event Title Duplicate",
            message="Test Event Message Duplicate",
            dedup_key="unique_test_123"
        )
        assert act2 is not None
        assert act2.id == act1.id
    finally:
        db.close()


def test_activities_api_endpoints():
    response = client.get("/api/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    count_res = client.get("/api/activities/unread-count")
    assert count_res.status_code == 200
    assert "unread_count" in count_res.json()

    read_all_res = client.post("/api/activities/read-all")
    assert read_all_res.status_code == 200


def test_scheduler_service_status():
    assert scraping_scheduler is not None
    assert hasattr(scraping_scheduler, "start")
    assert hasattr(scraping_scheduler, "shutdown")
