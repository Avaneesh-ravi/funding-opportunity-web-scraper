import re
import logging
from typing import Optional, List, Dict, Any, Tuple
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import trafilatura

from app.scrapers.base import ScrapedOpportunity, calculate_deadline_status
from app.scrapers.universal_engine.date_utils import extract_dates_from_text, parse_flexible_date
from app.scrapers.universal_engine.document_extractor import extract_pdf_data
from app.scrapers.universal_engine.http_client import SafeHttpClient

logger = logging.getLogger(__name__)

# Known agency mappings for popular Indian & international domains
KNOWN_AGENCIES = {
    "brns.res.in": "Board of Research in Nuclear Sciences (BRNS)",
    "dst.gov.in": "Department of Science and Technology (DST)",
    "onlinedst.gov.in": "Department of Science and Technology (DST)",
    "dbtindia.gov.in": "Department of Biotechnology (DBT)",
    "icmr.nic.in": "Indian Council of Medical Research (ICMR)",
    "icmr.gov.in": "Indian Council of Medical Research (ICMR)",
    "csir.res.in": "Council of Scientific and Industrial Research (CSIR)",
    "serb.gov.in": "Science and Engineering Research Board (SERB)",
    "anrfindia.gov.in": "Anusandhan National Research Foundation (ANRF)",
    "ugc.ac.in": "University Grants Commission (UGC)",
    "aicte-india.org": "All India Council for Technical Education (AICTE)",
    "isro.gov.in": "Indian Space Research Organisation (ISRO)",
    "drdo.gov.in": "Defence Research and Development Organisation (DRDO)",
    "nih.gov": "National Institutes of Health (NIH)",
    "nsf.gov": "National Science Foundation (NSF)",
    "cordis.europa.eu": "European Commission (Horizon Europe)",
}

STRONG_GRANT_KEYWORDS = [
    "call for proposals",
    "call for research proposals",
    "request for proposals",
    "call for",
    "research grant",
    "funding opportunity",
    "project proposal",
    "scheme guidelines",
    "fellowship",
    "extramural research",
    "invitation of proposals",
    "submission of proposals",
    "grant solicitation",
    "call for crp",
    "call for applications",
    "grants-in-aid",
    "research project",
    "collaborative projects",
    "quantum mission"
]

SECONDARY_KEYWORDS = [
    "deadline",
    "last date",
    "submission",
    "eligibility",
    "funding",
    "grant",
    "principal investigator",
    "project duration",
    "scheme",
    "mission",
    "initiative",
    "proposals",
    "collaborative"
]

DISQUALIFYING_PATTERNS = [
    re.compile(r"^(?:privacy\s+policy|terms\s+(?:of\s+service|and\s+conditions)|disclaimer|about\s+us|contact\s+us|sitemap|copyright|sign\s+in|login)$", re.IGNORECASE)
]


def infer_funding_agency(url: str, meta_site_name: Optional[str] = None, soup: Optional[BeautifulSoup] = None) -> str:
    """
    Infers the funding agency or organization from domain, OpenGraph site_name, or page header.
    """
    try:
        host = urlparse(url).hostname or ""
        host_lower = host.lower()
        for domain_key, agency_name in KNOWN_AGENCIES.items():
            if host_lower == domain_key or host_lower.endswith("." + domain_key):
                return agency_name

        if meta_site_name and len(meta_site_name.strip()) > 2:
            return meta_site_name.strip()

        # Check logo or banner heading
        if soup:
            header_el = soup.find(["header", "nav"]) or soup
            brand_el = header_el.find(class_=re.compile(r"brand|logo|title|agency", re.IGNORECASE))
            if brand_el:
                brand_text = brand_el.get_text(strip=True)
                if 3 < len(brand_text) < 60:
                    return brand_text

        # Fallback to readable hostname
        parts = host_lower.replace("www.", "").split(".")
        if len(parts) >= 2:
            return parts[0].upper()
        return host or "External Portal"
    except Exception:
        return "Funding Organization"


def calculate_opportunity_confidence(title: str, text: str, has_deadline: bool, has_doc: bool) -> float:
    """
    Calculates extraction confidence (0.0 to 1.0) based on presence of funding terminology.
    """
    score = 0.0
    combined = (title + " " + text[:2000]).lower()

    # Check strong keywords
    strong_hits = sum(1 for kw in STRONG_GRANT_KEYWORDS if kw in combined)
    score += min(strong_hits * 0.25, 0.50)

    # Secondary keywords
    sec_hits = sum(1 for kw in SECONDARY_KEYWORDS if kw in combined)
    score += min(sec_hits * 0.08, 0.25)

    if has_deadline:
        score += 0.15
    if has_doc:
        score += 0.10

    # Penalize short or vague titles
    if len(title.strip()) < 10:
        score -= 0.2

    # Check disqualifiers
    if any(p.match(title.strip()) for p in DISQUALIFYING_PATTERNS):
        return 0.0

    return min(max(score, 0.0), 1.0)


def extract_opportunities_from_table(
    table_soup: BeautifulSoup,
    base_url: str,
    agency_name: str,
    http_client: SafeHttpClient
) -> List[ScrapedOpportunity]:
    """
    Extracts distinct funding opportunities from tabular rows (e.g. S.No, Title, Dates, PDF).
    """
    opportunities: List[ScrapedOpportunity] = []
    rows = table_soup.find_all("tr")
    if len(rows) < 2:
        return opportunities

    # Inspect headers
    headers = [th.get_text(" ", strip=True).lower() for th in rows[0].find_all(["th", "td"])]
    has_date_col = any("date" in h or "deadline" in h for h in headers)
    has_title_col = any("title" in h or "name" in h or "scheme" in h or "description" in h or "subject" in h or "call" in h for h in headers)

    start_col_idx = None
    deadline_col_idx = None
    title_col_idx = None
    for idx, h in enumerate(headers):
        if any(w in h for w in ("closing", "deadline", "last date", "end date")):
            deadline_col_idx = idx
        elif any(w in h for w in ("start", "opening", "announced", "issue date", "advertisement")):
            start_col_idx = idx
        elif any(w in h for w in ("title", "scheme", "call", "project", "subject", "name")):
            if title_col_idx is None:
                title_col_idx = idx

    # Process data rows
    for row in rows[1:]:
        cells = row.find_all("td")
        if len(cells) < 2:
            continue

        row_text = " ".join(c.get_text(" ", strip=True) for c in cells)
        if len(row_text) < 15:
            continue

        # Find document link in row
        doc_url = None
        for a_tag in row.find_all("a", href=True):
            href = a_tag["href"]
            if href.lower().endswith((".pdf", ".docx", ".doc")):
                doc_url = urljoin(base_url, href)
                break

        # Find opportunity title
        title_cell = None
        if title_col_idx is not None and title_col_idx < len(cells):
            t_text = cells[title_col_idx].get_text(" ", strip=True)
            if len(t_text) > 8:
                title_cell = t_text

        if not title_cell:
            for cell in cells:
                cell_text = cell.get_text(" ", strip=True)
                if len(cell_text) > 15 and not any(char.isdigit() for char in cell_text[:3]):
                    title_cell = cell_text
                    break
        if not title_cell:
            title_cell = cells[1].get_text(" ", strip=True) if len(cells) > 1 else cells[0].get_text(" ", strip=True)

        if len(title_cell) < 10:
            continue

        # Extract dates from explicit date columns if present
        announcement_date = None
        deadline_date = None
        if start_col_idx is not None and start_col_idx < len(cells):
            announcement_date = parse_flexible_date(cells[start_col_idx].get_text(" ", strip=True))
        if deadline_col_idx is not None and deadline_col_idx < len(cells):
            deadline_date = parse_flexible_date(cells[deadline_col_idx].get_text(" ", strip=True))

        # Fallback to extracting from row text
        if not announcement_date or not deadline_date:
            a_d, d_d = extract_dates_from_text(row_text)
            if not announcement_date:
                announcement_date = a_d
            if not deadline_date:
                deadline_date = d_d

        # Check confidence
        conf = calculate_opportunity_confidence(title_cell, row_text, bool(deadline_date), bool(doc_url))
        if has_date_col or has_title_col:
            conf += 0.15

        if conf >= 0.35:
            deadline_status = calculate_deadline_status(
                opening_date=announcement_date,
                current_deadline=deadline_date
            )
            opp = ScrapedOpportunity(
                title=title_cell[:500],
                funding_agency=agency_name,
                announcement_date=announcement_date,
                opening_date=announcement_date,
                original_deadline=deadline_date,
                current_deadline=deadline_date,
                deadline_status=deadline_status,
                document_url=doc_url,
                source_url=base_url,
                description=row_text[:1000]
            )
            opportunities.append(opp)

    return opportunities


def extract_single_page_opportunity(
    soup: BeautifulSoup,
    url: str,
    agency_name: str,
    meta_info: Dict[str, Any],
    http_client: SafeHttpClient
) -> Optional[ScrapedOpportunity]:
    """
    Extracts a primary opportunity from a detailed funding call page.
    """
    html_str = str(soup)
    
    # 1. Clean main content text using Trafilatura
    body_text = trafilatura.extract(html_str, include_tables=True, include_links=True) or ""
    if not body_text.strip():
        body_text = soup.get_text(" ", strip=True)

    # 2. Extract Title
    title = meta_info.get("title")
    h1 = soup.find("h1")
    if h1 and len(h1.get_text(strip=True)) > 8:
        title = h1.get_text(strip=True)
    elif not title:
        h2 = soup.find("h2")
        if h2:
            title = h2.get_text(strip=True)

    if not title:
        title = "Research Grant Call"

    # Clean title noise (e.g. "Home | Department of...", "| Portal")
    if "|" in title:
        title = title.split("|")[0].strip()
    if " - " in title and len(title.split(" - ")[0].strip()) > 10:
        title = title.split(" - ")[0].strip()

    # 3. Find attached document (PDF)
    doc_url = None
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if href.lower().endswith(".pdf"):
            # Check text of link for funding/guidelines keyword
            link_text = a_tag.get_text(strip=True).lower()
            doc_url = urljoin(url, href)
            if any(k in link_text for k in ("call", "guideline", "format", "proposal", "notification", "scheme")):
                break

    # 4. Extract dates from text and metadata
    announcement_date, deadline_date = extract_dates_from_text(body_text)
    if not announcement_date and meta_info.get("published_date"):
        announcement_date = meta_info["published_date"]
    if not deadline_date and meta_info.get("json_ld_deadline"):
        deadline_date = meta_info["json_ld_deadline"]

    # 5. Extract amount and eligibility if document is present and dates missing
    amount = None
    eligibility = None
    if doc_url:
        pdf_res = extract_pdf_data(doc_url, http_client)
        if pdf_res:
            if not deadline_date and pdf_res.get("deadline_date"):
                deadline_date = pdf_res["deadline_date"]
            if not announcement_date and pdf_res.get("announcement_date"):
                announcement_date = pdf_res["announcement_date"]
            amount = pdf_res.get("amount")
            eligibility = pdf_res.get("eligibility")

    # 6. Check JSON-LD grant schemas and funder
    for it in meta_info.get("json_ld_items", []):
        if isinstance(it, dict):
            funder = it.get("funder")
            if isinstance(funder, dict) and funder.get("name"):
                agency_name = funder["name"]
            elif isinstance(funder, str) and funder:
                agency_name = funder

    has_grant_schema = any(
        isinstance(it, dict) and str(it.get("@type", "")).lower() in ("grant", "fundingopportunity", "researchproject")
        for it in meta_info.get("json_ld_items", [])
    )

    # 7. Confidence verification
    conf = calculate_opportunity_confidence(title, body_text, bool(deadline_date), bool(doc_url))
    if has_grant_schema:
        conf += 0.35

    if conf < 0.35:
        # Not an actual funding opportunity (e.g. general About page or generic portal home)
        logger.info("Page at %s scored low confidence (%.2f); not classified as funding opportunity.", url, conf)
        return None

    deadline_status = calculate_deadline_status(
        opening_date=announcement_date,
        current_deadline=deadline_date
    )

    return ScrapedOpportunity(
        title=title[:500],
        funding_agency=agency_name,
        scheme_name=None,
        description=body_text[:2000] if body_text else meta_info.get("description"),
        announcement_date=announcement_date,
        opening_date=announcement_date,
        original_deadline=deadline_date,
        current_deadline=deadline_date,
        deadline_status=deadline_status,
        funding_amount=amount,
        eligibility=eligibility,
        document_url=doc_url,
        source_url=url
    )
