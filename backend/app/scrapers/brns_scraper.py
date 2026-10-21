import re
import io
from typing import Optional, Dict, Any
from urllib.parse import urljoin, parse_qs, urlparse
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

from app.scrapers.base import BaseScraper, ScrapedOpportunity, calculate_deadline_status
from app.config import settings

class BRNSScraper(BaseScraper):
    def __init__(self, user_agent: str = None):
        self.user_agent = user_agent or settings.DEFAULT_USER_AGENT
        self.headers = {"User-Agent": self.user_agent}

    def scrape(self, target_url: str, reference_now: datetime = None) -> ScrapedOpportunity:
        """
        Scrapes a BRNS opportunity page and its linked detail document PDF.
        """
        response = requests.get(target_url, headers=self.headers, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # 1. Extract external identifier (e.g. content_id=69)
        parsed_url = urlparse(target_url)
        qs = parse_qs(parsed_url.query)
        ext_id = qs.get("content_id", [None])[0] or "brns_69"
        
        # 2. Extract Title and Scheme/Phase
        main_content = soup.find("td", class_="content") or soup.body
        
        title_font = main_content.find("font", size=re.compile(r"[3-5]")) if main_content else None
        overall_title = title_font.get_text(strip=True) if title_font else "Call for Coordinated Research Projects (CRPs)"
        
        h2_tag = main_content.find("h2") if main_content else None
        phase_title = h2_tag.get_text(strip=True) if h2_tag else overall_title

        # Combine title if appropriate
        full_title = phase_title if phase_title else overall_title

        # 3. Extract Dates using regex patterns
        page_text = main_content.get_text(" ", strip=True) if main_content else soup.get_text(" ", strip=True)
        page_text = page_text.replace('\xa0', ' ')
        
        announcement_date = self._parse_date_regex(r"Announced\s+on\s*:\s*([A-Za-z]+\s+\d{1,2},\s*\d{4}|\d{1,2}\s+[A-Za-z]+\s+\d{4})", page_text)
        deadline_date = self._parse_date_regex(r"Last\s+Date\s+of\s+submission\s*:\s*([A-Za-z]+\s+\d{1,2},\s*\d{4}|\d{1,2}\s+[A-Za-z]+\s+\d{4})", page_text)
        
        # 4. Extract Detail Document URL
        doc_url = None
        for a_tag in soup.find_all("a", href=True):
            a_text = a_tag.get_text(strip=True)
            href = a_tag["href"]
            if "detail document" in a_text.lower() or href.endswith(".pdf") or "public_files" in href:
                doc_url = urljoin(target_url, href)
                break
        
        # 5. Supplementary extraction from PDF if available
        pdf_details = self._extract_pdf_details(doc_url) if doc_url else {}
        
        # Construct full description
        description_parts = []
        if pdf_details.get("objective"):
            description_parts.append(f"Objective: {pdf_details['objective']}")
        if pdf_details.get("summary"):
            description_parts.append(pdf_details["summary"])
        full_description = "\n\n".join(description_parts) if description_parts else f"Official BRNS announcement for {full_title}."

        # Calculate deadline status
        status = calculate_deadline_status(
            opening_date=announcement_date, # BRNS announcement date functions as effective opening
            current_deadline=deadline_date,
            reference_now=reference_now
        )
        
        return ScrapedOpportunity(
            title=full_title,
            external_identifier=f"BRNS_{ext_id}",
            scheme_name="Coordinated Research Projects (CRPs)",
            funding_agency="Board of Research in Nuclear Sciences (BRNS)",
            description=full_description,
            announcement_date=announcement_date,
            opening_date=announcement_date,
            original_deadline=deadline_date,
            current_deadline=deadline_date,
            deadline_status=status,
            funding_amount=pdf_details.get("funding_amount", "As per BRNS research grant norms (Equipment, Staff, Contingency, Travel)"),
            eligibility=pdf_details.get("eligibility", "Faculty / Regular Researchers in recognized Academic Institutions / Universities / National Laboratories in India."),
            research_areas=pdf_details.get("research_areas", "Nuclear Science, Plasma Physics, Chemical & Materials Sciences, Bio-Sciences, Electronics & Instrumentation."),
            project_duration=pdf_details.get("project_duration", "3 Years (standard CRP period)"),
            submission_instructions="Applications must be submitted online through the BRNS GMS Portal (gb_register.php / gb_login.php).",
            application_url=urljoin(target_url, "gb_login.php"),
            document_url=doc_url,
            source_url=target_url
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

    def _extract_pdf_details(self, pdf_url: str) -> dict:
        details = {}
        try:
            res = requests.get(pdf_url, headers=self.headers, timeout=15)
            if res.status_code == 200:
                pdf_bytes = res.content
                pdf_text = ""
                
                # Attempt PyMuPDF (fitz) first
                if fitz:
                    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                    for page in doc:
                        pdf_text += page.get_text() + "\n"
                elif pdfplumber:
                    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                        for page in pdf.pages:
                            pdf_text += (page.extract_text() or "") + "\n"

                if pdf_text:
                    details["summary"] = pdf_text[:1000].strip()
                    # Try finding eligibility or specific sections in PDF text
                    if "eligibility" in pdf_text.lower():
                        match = re.search(r"eligibility[^\n:]*[:\n]([^\n]+)", pdf_text, re.IGNORECASE)
                        if match:
                            details["eligibility"] = match.group(1).strip()
        except Exception as e:
            # If PDF fetch or parse fails, return empty details gracefully
            pass
        return details
