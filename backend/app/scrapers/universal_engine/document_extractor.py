import io
import re
import logging
from typing import Optional, Dict, Any
from urllib.parse import urljoin

from app.scrapers.universal_engine.date_utils import extract_dates_from_text
from app.scrapers.universal_engine.http_client import SafeHttpClient, MAX_PDF_SIZE_BYTES

logger = logging.getLogger(__name__)

AMOUNT_PATTERNS = [
    re.compile(r"(?:Rs\.?|INR|₹)\s*([0-9,]+(?:\.[0-9]{2})?\s*(?:Lakhs?|Crores?|Lakh|Cr)?)", re.IGNORECASE),
    re.compile(r"(\$\s*[0-9,]+(?:\.[0-9]{2})?\s*(?:Million|Billion|K)?)", re.IGNORECASE),
    re.compile(r"(?:budget|grant|funding\s+amount|financial\s+assistance)\s*(?:of|up\s+to|is|:)?\s*([₹$RsINR0-9,\.\s]+(?:Lakhs?|Crores?|Million)?)", re.IGNORECASE)
]

ELIGIBILITY_KEYWORDS = [
    re.compile(r"(?:eligibility(?:\s+criteria)?|who\s+can\s+apply|eligible\s+applicants?|target\s+beneficiaries?)\s*[:\-\n]([^\n\r]+(?:\n[^\n\r]+){1,4})", re.IGNORECASE)
]


def extract_pdf_data(pdf_url: str, http_client: SafeHttpClient) -> Optional[Dict[str, Any]]:
    """
    Downloads and inspects a linked PDF document using pdfplumber/PyMuPDF.
    Extracts text, deadlines, announcement dates, and grant amounts.
    """
    try:
        res = http_client.fetch(pdf_url, max_size=MAX_PDF_SIZE_BYTES, max_retries=0)
        if not res.content or len(res.content) < 100:
            return None

        pdf_bytes = io.BytesIO(res.content)
        extracted_pages = []
        is_scanned = False

        # Attempt extraction using pdfplumber first
        try:
            import pdfplumber
            with pdfplumber.open(pdf_bytes) as pdf:
                max_pages = min(len(pdf.pages), 10)
                for i in range(max_pages):
                    page_text = pdf.pages[i].extract_text() or ""
                    if page_text.strip():
                        extracted_pages.append(page_text.strip())
        except Exception as e:
            logger.debug("pdfplumber extraction failed on %s: %s; trying PyMuPDF", pdf_url, e)

        # Fallback to PyMuPDF (fitz) if needed
        if not extracted_pages:
            try:
                import fitz
                doc = fitz.open(stream=res.content, filetype="pdf")
                max_pages = min(len(doc), 10)
                for i in range(max_pages):
                    page_text = doc[i].get_text() or ""
                    if page_text.strip():
                        extracted_pages.append(page_text.strip())
            except Exception as e:
                logger.debug("PyMuPDF extraction failed on %s: %s", pdf_url, e)

        full_text = "\n\n".join(extracted_pages)
        if not full_text.strip():
            # Scanned PDF requiring OCR
            return {
                "document_url": pdf_url,
                "is_scanned": True,
                "text": "",
                "announcement_date": None,
                "deadline_date": None,
                "amount": None,
                "eligibility": None
            }

        # Extract dates from text
        announcement_date, deadline_date = extract_dates_from_text(full_text)

        # Extract funding amount
        amount = None
        for pattern in AMOUNT_PATTERNS:
            match = pattern.search(full_text)
            if match:
                candidate = match.group(1).strip()
                if len(candidate) > 2 and any(char.isdigit() for char in candidate):
                    amount = candidate
                    break

        # Extract eligibility snippet
        eligibility = None
        for pattern in ELIGIBILITY_KEYWORDS:
            match = pattern.search(full_text)
            if match:
                eligibility = match.group(1).strip()[:500]
                break

        return {
            "document_url": pdf_url,
            "is_scanned": False,
            "text": full_text[:4000],  # bounded text preview
            "announcement_date": announcement_date,
            "deadline_date": deadline_date,
            "amount": amount,
            "eligibility": eligibility
        }

    except Exception as e:
        logger.warning("Failed to extract data from PDF at %s: %s", pdf_url, e)
        return None
