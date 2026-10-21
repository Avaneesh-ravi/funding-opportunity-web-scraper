from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, Field

class WebsiteBase(BaseModel):
    name: str = Field(..., example="Board of Research in Nuclear Sciences (BRNS)")
    base_url: str = Field(..., example="https://brns.res.in")
    target_url: str = Field(..., example="https://brns.res.in/content_details.php?content_id=69")
    category: Optional[str] = "Research Grants"
    description: Optional[str] = None
    enabled: bool = True

class WebsiteCreate(WebsiteBase):
    pass

class WebsiteUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    target_url: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None

class WebsiteResponse(WebsiteBase):
    id: int
    scraper_type: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
