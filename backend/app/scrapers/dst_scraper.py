import re
import io
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin, parse_qs, urlparse
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from app.scrapers.base import BaseScraper, ScrapedOpportunity, calculate_deadline_status
from app.config import settings

class DSTScraper(BaseScraper):
    def __init__(self, user_agent: str = None):
        self.user_agent = user_agent or settings.DEFAULT_USER_AGENT
        self.headers = {"User-Agent": self.user_agent}

    def scrape(self, target_url: str, reference_now: datetime = None) -> ScrapedOpportunity:
        """
        Scrapes Department of Science and Technology (DST) e-PMS call for proposal listings and detail pages.
        """
        response = requests.get(target_url, headers=self.headers, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")

        # If target URL is the main announcement table, extract the first ongoing call or detail link
        if "frmnewannouncment" in target_url.lower() or "call-for-proposals" in target_url.lower():
            detail_link = None
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"]
                if "Projectproposalformat.aspx" in href or "call-for-proposals" in href:
                    detail_link = urljoin(target_url, href)
                    break
            
            if detail_link:
                return self._scrape_dst_detail_page(detail_link, reference_now=reference_now)
            else:
                # Scrape directly from announcement table row
                return self._scrape_dst_table_row(soup, target_url, reference_now=reference_now)
        else:
            # Scrape directly as a detail page
            return self._scrape_dst_detail_page(target_url, reference_now=reference_now)

    def _scrape_dst_detail_page(self, url: str, reference_now: datetime = None) -> ScrapedOpportunity:
        res = requests.get(url, headers=self.headers, timeout=20)
        res.raise_for_status()
        soup = BeautifulSoup(res.content, "html.parser")

        parsed_url = urlparse(url)
        qs = parse_qs(parsed_url.query)
        ext_id = qs.get("Id", [None])[0] or qs.get("id", [None])[0] or "dst_call"

        # Title extraction
        title = "DST Call for Project Proposals"
        
        # Check selected option in scheme dropdown first
        scheme_opt = soup.find("option", selected=True)
        if scheme_opt and len(scheme_opt.get_text(strip=True)) > 5 and not scheme_opt.get_text(strip=True).startswith("--"):
            title = scheme_opt.get_text(strip=True)
        else:
            title_a = soup.find("a", onclick=re.compile(r"OpenPopupById", re.IGNORECASE)) or soup.find("a", href=re.compile(r"Projectproposalformat\.aspx", re.IGNORECASE))
            if title_a:
                title = title_a.get_text(strip=True)

        # Division / Scheme extraction
        scheme_name = "Department of Science & Technology Scheme"
        span_div = soup.find("span", text=re.compile(r"Division|Programme|Department", re.IGNORECASE))
        if span_div:
            scheme_name = span_div.get_text(strip=True)

        # Dates extraction
        page_text = soup.get_text(" ", strip=True).replace('\xa0', ' ')
        announcement_date = self._parse_date_regex(r"(?:Start\s+Date|Announced\s+on|Opened\s+on)\s*:\s*([A-Za-z]+\s+\d{1,2},\s*\d{4}|\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{1,2}\s+[A-Za-z]+\s+\d{4})", page_text)
        deadline_date = self._parse_date_regex(r"(?:End\s+Date|Last\s+Date\s+of\s+submission|Closing\s+Date)\s*:\s*([A-Za-z]+\s+\d{1,2},\s*\d{4}|\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{1,2}\s+[A-Za-z]+\s+\d{4})", page_text)

        # Detail Document link resolution
        doc_url = None
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            a_text = a_tag.get_text(strip=True).lower()
            if "download" in a_text or href.endswith(".pdf") or href.endswith(".docx") or "Documents" in href:
                doc_url = urljoin(url, href)
                break

        # Description extraction
        desc_div = soup.find("id", re.compile(r"^des")) or soup.find("div", class_=re.compile(r"description|call-inner", re.IGNORECASE))
        description = desc_div.get_text(" ", strip=True) if desc_div else f"Official DST call for proposal: {title}."
        if len(description) < 20:
            description = f"DST e-PMS Portal proposal call: {title}. Refer to official guidelines for full eligibility and submission details."

        status = calculate_deadline_status(
            opening_date=announcement_date,
            current_deadline=deadline_date,
            reference_now=reference_now
        )

        return ScrapedOpportunity(
            title=title,
            external_identifier=f"DST_{ext_id}",
            scheme_name=scheme_name,
            funding_agency="Department of Science and Technology (DST)",
            description=description,
            announcement_date=announcement_date,
            opening_date=announcement_date,
            original_deadline=deadline_date,
            current_deadline=deadline_date,
            deadline_status=status,
            funding_amount="As per DST / e-PMS grant norms (Equipment, Manpower, Travel, Overhead)",
            eligibility="Faculty / Regular Researchers in recognized Academic Institutions, Universities, R&D Labs in India.",
            research_areas="Science & Technology, AI, Quantum, Materials, Energy, Climate & Interdisciplinary Research.",
            project_duration="3 Years (standard DST project duration)",
            submission_instructions="Proposals must be submitted online through the DST e-PMS Portal (https://onlinedst.gov.in).",
            application_url=urljoin(url, "login.aspx"),
            document_url=doc_url,
            source_url=url
        )

    def _scrape_dst_table_row(self, soup: BeautifulSoup, page_url: str, reference_now: datetime = None) -> ScrapedOpportunity:
        table = soup.find("table")
        title = "DST Call for Project Proposals"
        doc_url = None
        
        if table:
            first_a = table.find("a", href=True)
            if first_a:
                title = first_a.get_text(strip=True)
                doc_url = urljoin(page_url, first_a["href"])

        return ScrapedOpportunity(
            title=title,
            external_identifier="DST_EPMS_MAIN",
            scheme_name="Department of Science & Technology Scheme",
            funding_agency="Department of Science and Technology (DST)",
            description=f"DST e-PMS Portal proposal call: {title}.",
            announcement_date=None,
            opening_date=None,
            original_deadline=None,
            current_deadline=None,
            deadline_status="Unknown",
            funding_amount="As per DST grant norms",
            eligibility="Faculty & Researchers in recognized Indian R&D institutions.",
            research_areas="Science & Technology, Frontier Technologies.",
            project_duration="3 Years",
            submission_instructions="Submit online via DST e-PMS portal.",
            application_url=urljoin(page_url, "login.aspx"),
            document_url=doc_url,
            source_url=page_url
        )

    def _parse_date_regex(self, pattern: str, text: str) -> Optional[datetime]:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            date_str = match.group(1).strip()
            try:
                return date_parser.parse(date_str)
            except Exception:
                return None
        return None
