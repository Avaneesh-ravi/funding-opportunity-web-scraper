from typing import Union, List
from app.scrapers.base import BaseScraper, ScrapedOpportunity

class ScraperNotConfiguredError(Exception):
    """Legacy exception preserved for backwards compatibility."""
    pass

from app.scrapers.universal_engine.universal_scraper import UniversalScraper

class GenericScraper(UniversalScraper):
    """
    Generic scraper now backed by the Universal Adaptive Scraping Engine.
    Handles any arbitrary validated URL without requiring domain-specific scrapers.
    """
    pass
