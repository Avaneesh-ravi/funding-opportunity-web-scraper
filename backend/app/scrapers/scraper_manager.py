from typing import Union, Optional
from urllib.parse import urlparse
from app.scrapers.base import BaseScraper
from app.scrapers.brns_scraper import BRNSScraper
from app.scrapers.dst_scraper import DSTScraper
from app.scrapers.generic_scraper import GenericScraper


class ScraperManager:
    def __init__(self):
        self._scrapers = {
            "brns": BRNSScraper(),
            "dst": DSTScraper(),
        }

    @staticmethod
    def _extract_domain(target: str) -> str:
        """
        Extract normalized hostname/domain from a URL or domain string.
        """
        if not target:
            return ""
        cleaned = str(target).strip()
        if "://" not in cleaned and not cleaned.startswith("//"):
            cleaned = "https://" + cleaned
        try:
            parsed = urlparse(cleaned)
            host = (parsed.hostname or parsed.netloc or "").lower().strip()
            if ":" in host:
                host = host.split(":")[0]
            return host
        except Exception:
            return ""

    def is_dst_target(self, target_url_or_type_or_id: Union[str, int, None]) -> bool:
        """
        Reliably determines whether a given identifier, URL, scraper type,
        or website ID refers to the Department of Science and Technology (DST).
        """
        if target_url_or_type_or_id is None:
            return False

        # Registered website ID check (DST default seed ID is 2)
        if isinstance(target_url_or_type_or_id, int):
            return target_url_or_type_or_id == 2

        val = str(target_url_or_type_or_id).strip()
        if not val:
            return False

        if val == "2":
            return True

        val_lower = val.lower()
        if val_lower in ("dst", "dst_scraper", "onlinedst"):
            return True

        domain = self._extract_domain(val)
        if domain:
            if domain in ("dst.gov.in", "onlinedst.gov.in"):
                return True
            if domain.endswith(".dst.gov.in") or domain.endswith(".onlinedst.gov.in"):
                return True

        return False

    def is_brns_target(self, target_url_or_type_or_id: Union[str, int, None]) -> bool:
        """
        Reliably determines whether a given identifier, URL, scraper type,
        or website ID refers to the Board of Research in Nuclear Sciences (BRNS).
        """
        if target_url_or_type_or_id is None:
            return False

        # Registered website ID check (BRNS default seed ID is 1)
        if isinstance(target_url_or_type_or_id, int):
            return target_url_or_type_or_id == 1

        val = str(target_url_or_type_or_id).strip()
        if not val:
            return False

        if val == "1":
            return True

        val_lower = val.lower()
        if val_lower in ("brns", "brns_scraper"):
            return True

        domain = self._extract_domain(val)
        if domain:
            if domain == "brns.res.in" or domain.endswith(".brns.res.in"):
                return True

        return False

    def get_scraper_type(self, target_url_or_type_or_id: Union[str, int, None]) -> str:
        """
        Determines the scraper type identifier ("brns", "dst", or "generic")
        for a given URL, scraper key, or registered website ID.
        """
        if self.is_brns_target(target_url_or_type_or_id):
            return "brns"
        elif self.is_dst_target(target_url_or_type_or_id):
            return "dst"
        return "generic"

    def get_scraper(
        self,
        target_url_or_type: Union[str, int, None],
        scraper_type: Optional[str] = None,
        website_id: Optional[int] = None
    ) -> BaseScraper:
        """
        Returns the appropriate scraper instance for the given target URL,
        scraper type, or registered website ID.
        """
        # 1. Check explicit scraper_type if provided
        if scraper_type:
            stype = self.get_scraper_type(scraper_type)
            if stype == "brns":
                return BRNSScraper()
            elif stype == "dst":
                return DSTScraper()

        # 2. Check website_id if provided
        if website_id is not None:
            stype = self.get_scraper_type(website_id)
            if stype == "brns":
                return BRNSScraper()
            elif stype == "dst":
                return DSTScraper()

        # 3. Check target_url_or_type
        stype = self.get_scraper_type(target_url_or_type)
        if stype == "brns":
            return BRNSScraper()
        elif stype == "dst":
            return DSTScraper()

        return GenericScraper()


scraper_manager = ScraperManager()

