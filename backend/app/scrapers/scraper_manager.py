from urllib.parse import urlparse
from app.scrapers.base import BaseScraper
from app.scrapers.brns_scraper import BRNSScraper
from app.scrapers.dst_scraper import DSTScraper
from app.scrapers.generic_scraper import GenericScraper

class ScraperManager:
    def __init__(self):
        self._scrapers = {
            "brns.res.in": BRNSScraper(),
            "brns": BRNSScraper(),
            "dst.gov.in": DSTScraper(),
            "onlinedst.gov.in": DSTScraper(),
            "dst": DSTScraper(),
        }

    def get_scraper_type(self, url_or_type: str) -> str:
        """
        Determines the scraper type identifier for a given URL or key.
        """
        url_lower = url_or_type.lower()
        if "brns.res.in" in url_lower or url_lower == "brns":
            return "brns"
        elif "dst.gov.in" in url_lower or "onlinedst.gov.in" in url_lower or url_lower == "dst":
            return "dst"
        return "generic"

    def get_scraper(self, target_url_or_type: str) -> BaseScraper:
        """
        Returns the appropriate scraper instance for the given target URL or scraper type.
        """
        parsed = urlparse(target_url_or_type)
        netloc = parsed.netloc.lower()
        url_lower = target_url_or_type.lower()
        
        if "brns.res.in" in netloc or "brns" in url_lower:
            return BRNSScraper()
        elif "dst.gov.in" in netloc or "onlinedst.gov.in" in netloc or "dst" in url_lower:
            return DSTScraper()
        
        return GenericScraper()

scraper_manager = ScraperManager()
