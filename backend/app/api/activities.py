from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.activity import Activity
from app.schemas.activity import ActivityResponse, ActivityMarkRead

router = APIRouter(prefix="/activities", tags=["In-Website Activities & Notifications"])

@router.get("", response_model=List[ActivityResponse])
def get_activities(
    unread_only: bool = Query(False, description="Filter only unread notifications"),
    limit: int = Query(50, description="Max activities to return"),
    db: Session = Depends(get_db)
):
    """
    Get in-website activity logs and notifications sorted by most recent first.
    """
    query = db.query(Activity)
    if unread_only:
        query = query.filter(Activity.is_read == False)
    return query.order_by(Activity.created_at.desc()).limit(limit).all()


@router.get("/unread-count")
def get_unread_count(db: Session = Depends(get_db)):
    """
    Returns unread notification badge count.
    """
    count = db.query(Activity).filter(Activity.is_read == False).count()
    return {"unread_count": count}


@router.patch("/{activity_id}/read", response_model=ActivityResponse)
def mark_activity_as_read(activity_id: int, mark_in: ActivityMarkRead, db: Session = Depends(get_db)):
    """
    Mark an individual notification as read or unread.
    """
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity notification not found.")
    
    activity.is_read = mark_in.is_read
    db.commit()
    db.refresh(activity)
    return activity


@router.post("/read-all")
def mark_all_activities_as_read(db: Session = Depends(get_db)):
    """
    Mark all unread notifications as read.
    """
    db.query(Activity).filter(Activity.is_read == False).update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read."}
