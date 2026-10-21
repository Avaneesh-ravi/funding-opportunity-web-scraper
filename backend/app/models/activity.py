from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("websites.id", ondelete="SET NULL"), nullable=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="SET NULL"), nullable=True)
    event_type = Column(String(50), nullable=False, index=True) 
    # Types: NEW_OPPORTUNITY, DEADLINE_CHANGED, EXTENSION_VERIFIED, UPCOMING_DEADLINE, SCRAPE_SUCCESS, SCRAPE_FAILED, CONFIG_REQUIRED
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, index=True)
    event_hash = Column(String(255), unique=True, index=True, nullable=True) # Deduplication key
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    website = relationship("Website", foreign_keys=[website_id])
    opportunity = relationship("Opportunity", foreign_keys=[opportunity_id])
