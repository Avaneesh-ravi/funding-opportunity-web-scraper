from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ScrapeRunResponse(BaseModel):
    id: int
    website_id: int
    started_at: datetime
    finished_at: Optional[datetime] = None
    status: str
    records_found: int = 0
    records_created: int = 0
    records_updated: int = 0
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
