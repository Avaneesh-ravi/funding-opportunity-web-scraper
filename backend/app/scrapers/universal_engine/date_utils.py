import re
import logging
from datetime import datetime
from typing import Optional, Tuple
from dateutil import parser as dateutil_parser

logger = logging.getLogger(__name__)

# Precompiled regex patterns for common date expressions in Indian and global research portals
DEADLINE_PATTERNS = [
    re.compile(
        r"(?:last\s+date\s*(?:for|of)?\s*(?:submission(?:\s+of\s+[a-z/]+)?|receiving|receipt|applying|registration|proposals?|comments?|suggestions?|feedback)?"
        r"|submission\s+deadline|deadline\s+for\s+(?:submission(?:\s+of\s+[a-z/]+)?|suggestions?|feedback|comments?|proposals?)"
        r"|closing\s+date|application\s+deadline|due\s+date|valid\s+up\s*to|cut[- ]off\s+date|deadline|closing)"
        r"\s*(?:is|:|-)?\s*(?:(?:\d{1,2}:\d{2}(?::\d{2})?\s*(?:am|pm|hrs|hours)?|\d{1,2}\s*(?:am|pm|hrs|hours))\s*(?:on|by|before|till)?\s*|(?:on|by|before|till)\s+)?"
        r"([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4}"
        r"|[0-9]{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+[0-9]{4}"
        r"|[A-Za-z]+\s+[0-9]{1,2}(?:st|nd|rd|th)?,\s*[0-9]{4}"
        r"|[0-9]{1,2}-[A-Za-z]{3}-[0-9]{2,4})",
        re.IGNORECASE
    ),
    re.compile(
        r"(?:deadline|closing)\s*:\s*(?:(?:\d{1,2}:\d{2}(?::\d{2})?\s*(?:am|pm|hrs|hours)?|\d{1,2}\s*(?:am|pm|hrs|hours))\s*(?:on|by|before|till)?\s*|(?:on|by|before|till)\s+)?"
        r"([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4}|[A-Za-z]+\s+[0-9]{1,2},\s*[0-9]{4}|[0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4})",
        re.IGNORECASE
    )
]

ANNOUNCEMENT_PATTERNS = [
    re.compile(
        r"(?:announced\s+on|opening\s+date|published\s+on|start\s+date|call\s+opens|date\s+of\s+issue|advertisement\s+date|notified\s+on)"
        r"\s*(?:is|:|-)?\s*"
        r"([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4}"
        r"|[0-9]{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+[0-9]{4}"
        r"|[A-Za-z]+\s+[0-9]{1,2}(?:st|nd|rd|th)?,\s*[0-9]{4}"
        r"|[0-9]{1,2}-[A-Za-z]{3}-[0-9]{2,4})",
        re.IGNORECASE
    )
]

STANDALONE_DATE_PATTERN = re.compile(
    r"\b([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{4}|[0-9]{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+[0-9]{4})\b",
    re.IGNORECASE
)


def parse_flexible_date(date_string: Optional[str]) -> Optional[datetime]:
    """
    Parses a string into a valid datetime object.
    Supports DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD, and textual formats.
    Returns None if unparseable or outside realistic grant years (2020-2035).
    """
    if not date_string or not isinstance(date_string, str):
        return None

    cleaned = date_string.strip()
    # Strip ordinal suffixes: 1st, 2nd, 3rd, 4th
    cleaned = re.sub(r"(\d{1,2})(st|nd|rd|th)", r"\1", cleaned, flags=re.IGNORECASE)
    # Strip explicit times or timezone words at the end if attached
    cleaned = re.sub(
        r"\s*(?:at|by|upto|up\s+to|till|before)?\s*(?:\d{1,2}:\d{2}(?::\d{2})?\s*(?:hrs|hours|pm|am|ist)?|\d{1,2}\s*(?:hrs|hours|pm|am|ist))\s*$",
        "",
        cleaned,
        flags=re.IGNORECASE
    ).strip()

    if not cleaned or len(cleaned) < 6:
        return None

    # Try parsing with dayfirst=True (standard in India, UK, Europe)
    parsed_dt = None
    try:
        parsed_dt = dateutil_parser.parse(cleaned, dayfirst=True, fuzzy=True)
    except Exception:
        try:
            parsed_dt = dateutil_parser.parse(cleaned, dayfirst=False, fuzzy=True)
        except Exception:
            parsed_dt = None

    if parsed_dt:
        # Validate year bounds
        if 2020 <= parsed_dt.year <= 2035:
            return parsed_dt

    return None


def extract_dates_from_text(text: str) -> Tuple[Optional[datetime], Optional[datetime]]:
    """
    Scans a block of text for announcement and deadline dates.
    Returns (announcement_date, deadline_date).
    """
    if not text:
        return (None, None)

    announcement_date = None
    deadline_date = None

    # Search for deadline
    for pattern in DEADLINE_PATTERNS:
        match = pattern.search(text)
        if match:
            candidate = match.group(1)
            parsed = parse_flexible_date(candidate)
            if parsed:
                deadline_date = parsed
                break

    # Search for announcement date
    for pattern in ANNOUNCEMENT_PATTERNS:
        match = pattern.search(text)
        if match:
            candidate = match.group(1)
            parsed = parse_flexible_date(candidate)
            if parsed:
                announcement_date = parsed
                break

    return (announcement_date, deadline_date)
