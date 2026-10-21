import logging
from typing import List, Optional, Union
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from app.scrapers.base import BaseScraper, ScrapedOpportunity, calculate_deadline_status
from app.scrapers.universal_engine.http_client import SafeHttpClient, SafeResponse
from app.scrapers.universal_engine.metadata_extractor import extract_html_metadata, parse_feed_content
from app.scrapers.universal_engine.document_extractor import extract_pdf_data
from app.scrapers.universal_engine.browser_fallback import is_spa_shell, render_with_browser_if_available
from app.scrapers.universal_engine.crawler import discover_relevant_links
from app.scrapers.universal_engine.opportunity_classifier import (
    infer_funding_agency,
    extract_opportunities_from_table,
    extract_single_page_opportunity,
    calculate_opportunity_confidence
)

logger = logging.getLogger(__name__)


class UniversalScraper(BaseScraper):
    """
    Universal Adaptive Scraping Engine.
    Employs a layered extraction pipeline:
      - Layer A: Safe HTTP streaming with SSRF protection on all hops and bounded size.
      - Layer B: Generic HTML & structured-data extraction (Trafilatura, JSON-LD, OpenGraph).
      - Layer C: Bounded link discovery and crawl of relevant child detail pages.
      - Layer D: JavaScript SPA shell detection and headless browser rendering fallback.
      - Layer E: PDF document extraction with pdfplumber / PyMuPDF.
    """

    def __init__(self, user_agent: Optional[str] = None):
        self.http_client = SafeHttpClient(user_agent=user_agent)

    def scrape(self, target_url: str) -> Union[ScrapedOpportunity, List[ScrapedOpportunity]]:
        """
        Main entry point for scraping an arbitrary funding URL.
        Returns a list of ScrapedOpportunity objects (or single instance if exactly one found).
        """
        results = self.scrape_all(target_url)
        if not results:
            # Return an empty list or raise if needed by specific callers
            return []
        if len(results) == 1:
            return results[0]
        return results

    def scrape_all(self, target_url: str) -> List[ScrapedOpportunity]:
        """
        Extracts all qualifying funding opportunities from target_url and its top linked details.
        """
        url = target_url.strip()
        logger.info("UniversalScraper: starting adaptive extraction for %s", url)

        # ── 1. Fetch Target URL ──────────────────────────────────────────────
        try:
            res: SafeResponse = self.http_client.fetch(url)
        except Exception as e:
            logger.error("UniversalScraper: Failed fetching %s: %s", url, e)
            raise e

        agency_name = infer_funding_agency(url)

        # ── 2. Handle Direct PDF Document ───────────────────────────────────
        if res.is_pdf:
            logger.info("UniversalScraper: Target is a direct PDF document")
            pdf_data = extract_pdf_data(url, self.http_client)
            if pdf_data:
                deadline_status = calculate_deadline_status(
                    opening_date=pdf_data.get("announcement_date"),
                    current_deadline=pdf_data.get("deadline_date")
                )
                title = f"{agency_name} Research Notification"
                if pdf_data.get("text"):
                    # First line or sentence as title if reasonable
                    first_line = pdf_data["text"].split("\n")[0].strip()
                    if 15 < len(first_line) < 200:
                        title = first_line

                opp = ScrapedOpportunity(
                    title=title,
                    funding_agency=agency_name,
                    announcement_date=pdf_data.get("announcement_date"),
                    opening_date=pdf_data.get("announcement_date"),
                    original_deadline=pdf_data.get("deadline_date"),
                    current_deadline=pdf_data.get("deadline_date"),
                    deadline_status=deadline_status,
                    funding_amount=pdf_data.get("amount"),
                    eligibility=pdf_data.get("eligibility"),
                    document_url=url,
                    source_url=url,
                    description=pdf_data.get("text", "")[:1000]
                )
                return [opp]
            return []

        # ── 3. Handle RSS/Atom Feeds ────────────────────────────────────────
        if res.is_feed:
            logger.info("UniversalScraper: Target is an RSS/Atom feed")
            feed_items = parse_feed_content(res.text)
            feed_opps = []
            for item in feed_items:
                if calculate_opportunity_confidence(item["title"], item.get("summary", ""), False, False) >= 0.25:
                    opp = ScrapedOpportunity(
                        title=item["title"][:500],
                        funding_agency=agency_name,
                        announcement_date=item.get("published_date"),
                        opening_date=item.get("published_date"),
                        deadline_status="Unknown",
                        source_url=item.get("link") or url,
                        description=item.get("summary", "")[:1000]
                    )
                    feed_opps.append(opp)
            return feed_opps

        # ── 4. Parse HTML and Detect SPA Shell ──────────────────────────────
        html_content = res.text
        soup = BeautifulSoup(html_content, "html.parser")
        body_text_len = len(soup.get_text(strip=True))

        if is_spa_shell(html_content, body_text_len):
            logger.info("UniversalScraper: Empty SPA shell detected; attempting browser rendering")
            rendered_html, note = render_with_browser_if_available(url)
            if rendered_html:
                html_content = rendered_html
                soup = BeautifulSoup(html_content, "html.parser")
            else:
                logger.info("UniversalScraper browser fallback note: %s", note)

        # ── 5. Extract Structured Metadata ──────────────────────────────────
        meta_info = extract_html_metadata(soup)
        if meta_info.get("site_name"):
            agency_name = meta_info["site_name"]

        discovered_opportunities: List[ScrapedOpportunity] = []

        # ── 6. Strategy A: Tabular Opportunity Listings ─────────────────────
        tables = soup.find_all("table")
        for tbl in tables:
            tbl_opps = extract_opportunities_from_table(tbl, url, agency_name, self.http_client)
            if tbl_opps:
                discovered_opportunities.extend(tbl_opps)

        # ── 7. Strategy B: Single Detail Page Extraction ────────────────────
        if not discovered_opportunities:
            single_opp = extract_single_page_opportunity(soup, url, agency_name, meta_info, self.http_client)
            if single_opp:
                discovered_opportunities.append(single_opp)

        # ── 8. Strategy C: Link Discovery & Child Crawling ──────────────────
        # If we found 0 opportunities (or only 1 generic call from an index), crawl top child links
        if len(discovered_opportunities) <= 1:
            child_links = discover_relevant_links(soup, url, max_links=4)
            for child_url, anchor_text in child_links:
                try:
                    c_res = self.http_client.fetch(child_url)
                    if c_res.is_pdf:
                        pdf_data = extract_pdf_data(child_url, self.http_client)
                        if pdf_data:
                            dl_status = calculate_deadline_status(
                                opening_date=pdf_data.get("announcement_date"),
                                current_deadline=pdf_data.get("deadline_date")
                            )
                            c_opp = ScrapedOpportunity(
                                title=anchor_text[:300] if len(anchor_text) > 15 else f"{agency_name} Project Call",
                                funding_agency=agency_name,
                                announcement_date=pdf_data.get("announcement_date"),
                                opening_date=pdf_data.get("announcement_date"),
                                original_deadline=pdf_data.get("deadline_date"),
                                current_deadline=pdf_data.get("deadline_date"),
                                deadline_status=dl_status,
                                funding_amount=pdf_data.get("amount"),
                                eligibility=pdf_data.get("eligibility"),
                                document_url=child_url,
                                source_url=url,
                                description=pdf_data.get("text", "")[:1000]
                            )
                            discovered_opportunities.append(c_opp)
                    elif c_res.is_html:
                        c_soup = BeautifulSoup(c_res.text, "html.parser")
                        c_meta = extract_html_metadata(c_soup)
                        c_opp = extract_single_page_opportunity(c_soup, child_url, agency_name, c_meta, self.http_client)
                        if c_opp and not any(o.title == c_opp.title for o in discovered_opportunities):
                            discovered_opportunities.append(c_opp)
                except Exception as e:
                    logger.debug("Failed crawling child link %s: %s", child_url, e)

        # ── 9. Deduplication & Final Validation ─────────────────────────────
        unique_opps: List[ScrapedOpportunity] = []
        seen_titles = set()
        for opp in discovered_opportunities:
            norm_title = opp.title.strip().lower()
            if norm_title not in seen_titles:
                seen_titles.add(norm_title)
                unique_opps.append(opp)

        logger.info(
            "UniversalScraper: Completed extraction for %s. Found %d opportunity records.",
            url,
            len(unique_opps)
        )
        return unique_opps
