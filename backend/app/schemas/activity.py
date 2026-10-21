from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ActivityResponse(BaseModel):
    id: int
    website_id: Optional[int] = None
    opportunity_id: Optional[int] = None
    event_type: str
    title: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ActivityMarkRead(BaseModel):
    is_read: bool = True
