# Web Scraping Dashboard — BRNS Funding Opportunity Tracker

A full-stack web application that extracts, tracks, and manages funding opportunities, project announcements, submission deadlines, and official detail documents from the **Board of Research in Nuclear Sciences (BRNS)** (`https://brns.res.in/content_details.php?content_id=69`) and supports adding future funding portal URLs.

---

## Key Features

- **Dynamic BRNS Scraping Engine**: Automatically parses HTML content, announcement dates (`May 20, 2026`), submission deadlines (`August 31, 2026`), and linked official PDF detail documents (`BRNS_Announcement_for_CRP-2026_Phase1.pdf`).
- **PDF Detail Document Processing**: Downloads and extracts text from linked PDF announcements using `PyMuPDF` / `pdfplumber` for eligibility, research areas, and funding terms.
- **Deadline Status Logic & Precedence**: Evaluates status (`Closed`, `Closing Soon`, `Open`, `Upcoming`, `Extended`, `Unknown`, `Verification Required`) against current timezone (`Asia/Kolkata`). Expired deadlines (e.g. Aug 31, 2026 vs Oct 9, 2026) are cleanly identified as **Closed / Deadline Passed**.
- **Audit History Log**: Preserves original deadlines and records any field updates in an `opportunity_history` database table.
- **Add URL Interface**: Prominent `+ Add URL` feature with SSRF security validation. Unsupported websites report `"Scraper not configured"` when scraped without fabricating false records.
- **Reports & Export**: One-click CSV and Microsoft Excel (.xlsx) export of verified opportunities.
- **Modern Dashboard UI**: Built with React, TypeScript, Vite, Tailwind CSS, Lucide icons, responsive two-column detail panels, and real-time status counters.

---

## Technology Stack

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, Pydantic, Requests, BeautifulSoup4, PyMuPDF / pdfplumber, Pandas, OpenPyXL
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons
- **Database**: SQLite (`data/dashboard.db`)

---

## Installation & Setup Instructions

### 1. Prerequisites
- Python 3.10+ installed
- Node.js 18+ and npm installed

### 2. Backend Setup
```bash
# Navigate to project directory
cd d:/Project/backend

# Create virtual environment (optional but recommended)
python -m venv venv
# Windows activate:
venv\Scripts\activate

# Install backend dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd d:/Project/frontend

# Install npm dependencies
npm install
```

---

## Running the Application Locally

### Step 1: Start FastAPI Backend Server
```bash
cd d:/Project/backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend API will run at `http://127.0.0.1:8000`. API docs available at `http://127.0.0.1:8000/docs`.

### Step 2: Start React Vite Frontend Server
```bash
cd d:/Project/frontend
npm run dev
```
The web dashboard will run at `http://localhost:5173`.

---

## Automated Tests

Run the backend test suite:
```bash
cd d:/Project/backend
python -m pytest tests/ -v
```

Tests cover:
- `test_deadline_logic.py`: Deadline calculation status rules & precedence.
- `test_brns_scraper.py`: HTML parsing, regex date extraction, and PDF document link resolution.
- `test_api.py`: FastAPI endpoints, SSRF security validation, website creation, scrape trigger, and unsupported domain handling.

---

## API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | System health check and timezone |
| `GET` | `/api/websites` | List all registered website portals |
| `POST` | `/api/websites` | Register new target URL with SSRF check |
| `POST` | `/api/websites/{id}/scrape` | Trigger scraping for a specific website |
| `GET` | `/api/opportunities` | Search, filter, and sort opportunities |
| `GET` | `/api/opportunities/{id}` | Get opportunity details with audit log |
| `POST` | `/api/opportunities/{id}/refresh` | Re-scrape opportunity source URL |
| `GET` | `/api/opportunities/export` | Download CSV or Excel export |
| `GET` | `/api/scrape-runs` | View scraping execution history logs |
