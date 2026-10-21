import io
import pandas as pd
from typing import List
from app.models.opportunity import Opportunity

def export_opportunities_to_csv(opportunities: List[Opportunity]) -> io.BytesIO:
    """
    Exports a list of Opportunity database models to CSV BytesIO buffer.
    """
    data = []
    for index, opp in enumerate(opportunities, 1):
        data.append({
            "S.No.": index,
            "ID": opp.id,
            "Funding Agency": opp.funding_agency,
            "Opportunity Title": opp.title,
            "Scheme Name": opp.scheme_name or "N/A",
            "Announcement Date": opp.announcement_date.strftime("%Y-%m-%d") if opp.announcement_date else "Not specified",
            "Opening Date": opp.opening_date.strftime("%Y-%m-%d") if opp.opening_date else "Not specified",
            "Current Deadline": opp.current_deadline.strftime("%Y-%m-%d") if opp.current_deadline else "Not specified",
            "Original Deadline": opp.original_deadline.strftime("%Y-%m-%d") if opp.original_deadline else "Not specified",
            "Status": opp.deadline_status,
            "Eligibility": opp.eligibility or "Not specified",
            "Funding Amount": opp.funding_amount or "Not specified",
            "Research Areas": opp.research_areas or "Not specified",
            "Project Duration": opp.project_duration or "Not specified",
            "Detail Document URL": opp.document_url or "N/A",
            "Source URL": opp.source_url,
            "Last Checked": opp.last_verified_at.strftime("%Y-%m-%d %H:%M:%S") if opp.last_verified_at else "N/A",
        })
    
    df = pd.DataFrame(data)
    stream = io.BytesIO()
    df.to_csv(stream, index=False, encoding="utf-8-sig")
    stream.seek(0)
    return stream


def export_opportunities_to_excel(opportunities: List[Opportunity]) -> io.BytesIO:
    """
    Exports a list of Opportunity database models to Excel BytesIO buffer.
    """
    data = []
    for index, opp in enumerate(opportunities, 1):
        data.append({
            "S.No.": index,
            "ID": opp.id,
            "Funding Agency": opp.funding_agency,
            "Opportunity Title": opp.title,
            "Scheme Name": opp.scheme_name or "N/A",
            "Announcement Date": opp.announcement_date.strftime("%Y-%m-%d") if opp.announcement_date else "Not specified",
            "Opening Date": opp.opening_date.strftime("%Y-%m-%d") if opp.opening_date else "Not specified",
            "Current Deadline": opp.current_deadline.strftime("%Y-%m-%d") if opp.current_deadline else "Not specified",
            "Original Deadline": opp.original_deadline.strftime("%Y-%m-%d") if opp.original_deadline else "Not specified",
            "Status": opp.deadline_status,
            "Eligibility": opp.eligibility or "Not specified",
            "Funding Amount": opp.funding_amount or "Not specified",
            "Research Areas": opp.research_areas or "Not specified",
            "Project Duration": opp.project_duration or "Not specified",
            "Detail Document URL": opp.document_url or "N/A",
            "Source URL": opp.source_url,
            "Last Checked": opp.last_verified_at.strftime("%Y-%m-%d %H:%M:%S") if opp.last_verified_at else "N/A",
        })
    
    df = pd.DataFrame(data)
    stream = io.BytesIO()
    with pd.ExcelWriter(stream, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Funding Opportunities")
    stream.seek(0)
    return stream
