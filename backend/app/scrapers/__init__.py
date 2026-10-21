from app.scrapers.base import BaseScraper, ScrapedOpportunity, calculate_deadline_status
from app.scrapers.brns_scraper import BRNSScraper
from app.scrapers.dst_scraper import DSTScraper
from app.scrapers.generic_scraper import GenericScraper, ScraperNotConfiguredError
from app.scrapers.scraper_manager import scraper_manager, ScraperManager

__all__ = [
    "BaseScraper",
    "ScrapedOpportunity",
    "calculate_deadline_status",
    "BRNSScraper",
    "DSTScraper",
    "GenericScraper",
    "ScraperNotConfiguredError",
    "scraper_manager",
    "ScraperManager",
]
