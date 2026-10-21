from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class OpportunityHistoryResponse(BaseModel):
    id: int
    opportunity_id: int
    field_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_at: datetime
    verification_source: Optional[str] = None

    class Config:
        from_attributes = True


class OpportunityBase(BaseModel):
    title: str
    external_identifier: Optional[str] = None
    scheme_name: Optional[str] = None
    funding_agency: str = "BRNS"
    description: Optional[str] = None
    announcement_date: Optional[datetime] = None
    opening_date: Optional[datetime] = None
    original_deadline: Optional[datetime] = None
    current_deadline: Optional[datetime] = None
    deadline_status: str = "Unknown"
    funding_amount: Optional[str] = None
    eligibility: Optional[str] = None
    research_areas: Optional[str] = None
    project_duration: Optional[str] = None
    submission_instructions: Optional[str] = None
    application_url: Optional[str] = None
    document_url: Optional[str] = None
    source_url: str

class OpportunityResponse(OpportunityBase):
    id: int
    website_id: int
    first_seen_at: datetime
    last_seen_at: datetime
    last_verified_at: datetime
    created_at: datetime
    updated_at: datetime
    history: List[OpportunityHistoryResponse] = []

    class Config:
        from_attributes = True
