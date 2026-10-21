from datetime import datetime
import pytest
from app.scrapers.base import calculate_deadline_status

def test_deadline_status_closed_for_past_date():
    # Test C: Given deadline August 31, 2026 and reference date October 9, 2026 -> Closed
    ref_date = datetime(2026, 10, 9, 12, 0, 0)
    deadline = datetime(2026, 8, 31, 23, 59, 59)
    status = calculate_deadline_status(
        opening_date=datetime(2026, 5, 20),
        current_deadline=deadline,
        reference_now=ref_date
    )
    assert status == "Closed"

def test_deadline_status_open_for_future_date():
    ref_date = datetime(2026, 5, 25, 10, 0, 0)
    deadline = datetime(2026, 8, 31, 23, 59, 59)
    status = calculate_deadline_status(
        opening_date=datetime(2026, 5, 20),
        current_deadline=deadline,
        reference_now=ref_date
    )
    assert status == "Open"

def test_deadline_status_closing_soon():
    ref_date = datetime(2026, 8, 28, 10, 0, 0) # 3 days before Aug 31
    deadline = datetime(2026, 8, 31, 23, 59, 59)
    status = calculate_deadline_status(
        opening_date=datetime(2026, 5, 20),
        current_deadline=deadline,
        reference_now=ref_date
    )
    assert status == "Closing Soon"

def test_deadline_status_upcoming():
    ref_date = datetime(2026, 5, 10, 10, 0, 0) # Opening is May 20
    opening = datetime(2026, 5, 20, 0, 0, 0)
    deadline = datetime(2026, 8, 31, 23, 59, 59)
    status = calculate_deadline_status(
        opening_date=opening,
        current_deadline=deadline,
        reference_now=ref_date
    )
    assert status == "Upcoming"

def test_deadline_status_verification_required():
    status = calculate_deadline_status(
        opening_date=None,
        current_deadline=datetime(2026, 8, 31),
        verification_issue=True
    )
    assert status == "Verification Required"

def test_deadline_status_unknown_when_missing():
    status = calculate_deadline_status(
        opening_date=None,
        current_deadline=None
    )
    assert status == "Unknown"
