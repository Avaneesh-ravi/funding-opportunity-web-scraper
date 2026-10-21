import hashlib
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.activity import Activity

def create_activity_log(
    db: Session,
    event_type: str,
    title: str,
    message: str,
    website_id: Optional[int] = None,
    opportunity_id: Optional[int] = None,
    dedup_key: Optional[str] = None
) -> Optional[Activity]:
    """
    Creates an in-website activity notification with deduplication.
    Prevents duplicate entries when the same event is processed repeatedly.
    """
    event_hash = None
    if dedup_key:
        event_hash = hashlib.sha256(f"{event_type}_{dedup_key}".encode()).hexdigest()
        existing = db.query(Activity).filter(Activity.event_hash == event_hash).first()
        if existing:
            return existing

    activity = Activity(
        website_id=website_id,
        opportunity_id=opportunity_id,
        event_type=event_type,
        title=title,
        message=message,
        is_read=False,
        event_hash=event_hash,
        created_at=datetime.utcnow()
    )
    db.add(activity)
    try:
        db.commit()
        db.refresh(activity)
        return activity
    except Exception:
        db.rollback()
        return None
