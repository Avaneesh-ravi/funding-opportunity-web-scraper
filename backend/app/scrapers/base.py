from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict, Any, Union, List
import pytz

@dataclass
class ScrapedOpportunity:
    title: str
    external_identifier: Optional[str] = None
    scheme_name: Optional[str] = None
    funding_agency: str = "Board of Research in Nuclear Sciences (BRNS)"
    description: Optional[str] = None
    announcement_date: Optional[datetime] = None
    opening_date: Optional[datetime] = None
    original_deadline: Optional[datetime] = None
    current_deadline: Optional[datetime] = None
    deadline_status: str = "Unknown"
    funding_amount: Optional[str] = None
    eligibility: Optional[str] = None
    research_areas: Optional[str] = None
    project_duration: Optional[str] = None
    submission_instructions: Optional[str] = None
    application_url: Optional[str] = None
    document_url: Optional[str] = None
    source_url: str = ""
    is_extended: bool = False
    verification_issue: bool = False

def calculate_deadline_status(
    opening_date: Optional[datetime],
    current_deadline: Optional[datetime],
    is_extended: bool = False,
    verification_issue: bool = False,
    reference_now: Optional[datetime] = None,
    tz_name: str = "Asia/Kolkata"
) -> str:
    """
    Precedence rules for Deadline Status calculation:
    1. Verification Required for unresolved conflicts / issues.
    2. Unknown for missing or ambiguous deadlines.
    3. Closed for expired verified deadlines.
    4. Upcoming for verified future opening dates.
    5. Closing Soon for active opportunities closing within seven days.
    6. Extended if an official extension has been verified.
    7. Open for active accepting submissions.
    """
    if verification_issue:
        return "Verification Required"
    
    if not current_deadline:
        return "Unknown"

    tz = pytz.timezone(tz_name)
    if reference_now is None:
        reference_now = datetime.now(tz)
    elif reference_now.tzinfo is None:
        reference_now = tz.localize(reference_now)
    
    # Ensure current_deadline has timezone info for accurate comparison
    if current_deadline.tzinfo is None:
        current_deadline = tz.localize(current_deadline)
    
    # Ensure opening_date has timezone info if present
    if opening_date and opening_date.tzinfo is None:
        opening_date = tz.localize(opening_date)

    if current_deadline < reference_now:
        return "Closed"
    
    if opening_date and opening_date > reference_now:
        return "Upcoming"
    
    days_left = (current_deadline - reference_now).total_seconds() / (24 * 3600)
    if 0 <= days_left <= 7:
        return "Closing Soon"
    
    if is_extended:
        return "Extended"
    
    return "Open"


class BaseScraper(ABC):
    @abstractmethod
    def scrape(self, target_url: str) -> Union[ScrapedOpportunity, List[ScrapedOpportunity]]:
        """
        Scrape target URL and return a normalized ScrapedOpportunity instance or list of instances.
        """
        pass
