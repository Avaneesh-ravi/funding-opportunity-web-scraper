from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("websites.id", ondelete="CASCADE"), nullable=False)
    external_identifier = Column(String(255), nullable=True, index=True)
    title = Column(String(512), nullable=False)
    scheme_name = Column(String(255), nullable=True)
    funding_agency = Column(String(255), nullable=False, default="BRNS")
    description = Column(Text, nullable=True)
    announcement_date = Column(DateTime, nullable=True)
    opening_date = Column(DateTime, nullable=True)
    original_deadline = Column(DateTime, nullable=True)
    current_deadline = Column(DateTime, nullable=True)
    deadline_status = Column(String(50), nullable=False, default="Unknown")
    funding_amount = Column(Text, nullable=True)
    eligibility = Column(Text, nullable=True)
    research_areas = Column(Text, nullable=True)
    project_duration = Column(Text, nullable=True)
    submission_instructions = Column(Text, nullable=True)
    application_url = Column(String(512), nullable=True)
    document_url = Column(String(512), nullable=True)
    source_url = Column(String(512), nullable=False)
    first_seen_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)
    last_verified_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    website = relationship("Website", back_populates="opportunities")
    history = relationship("OpportunityHistory", back_populates="opportunity", cascade="all, delete-orphan")


class OpportunityHistory(Base):
    __tablename__ = "opportunity_history"

    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False)
    field_name = Column(String(100), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow)
    verification_source = Column(String(512), nullable=True)

    opportunity = relationship("Opportunity", back_populates="history")
