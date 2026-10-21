from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Website(Base):
    __tablename__ = "websites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    base_url = Column(String(512), nullable=False)
    target_url = Column(String(512), nullable=False, unique=True, index=True)
    category = Column(String(100), nullable=True, default="Research Grants")
    description = Column(Text, nullable=True)
    scraper_type = Column(String(50), nullable=False, default="brns")
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    opportunities = relationship("Opportunity", back_populates="website", cascade="all, delete-orphan")
    scrape_runs = relationship("ScrapeRun", back_populates="website", cascade="all, delete-orphan")
