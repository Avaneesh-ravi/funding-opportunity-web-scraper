from app.scrapers.base import BaseScraper, ScrapedOpportunity

class ScraperNotConfiguredError(Exception):
    """Raised when a website URL does not have a configured scraper implementation."""
    pass

class GenericScraper(BaseScraper):
    def scrape(self, target_url: str) -> ScrapedOpportunity:
        raise ScraperNotConfiguredError(f"Scraper not configured for target URL: {target_url}")
