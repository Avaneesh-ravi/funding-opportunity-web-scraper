import os
import sys
import time
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import imageio
from gtts import gTTS
import pyttsx3

OUTPUT_DIR = r"D:\Project\Funding Opportunity Web Scraper\output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

FINAL_MP4_PATH = os.path.join(OUTPUT_DIR, "Web_Scraping_Dashboard_Explanation.mp4")
SRT_PATH = os.path.join(OUTPUT_DIR, "Web_Scraping_Dashboard_Explanation.srt")

# Scenes definition matching storyboard
SCENES = [
    {
        "id": 1,
        "title": "Web Scraping Dashboard & Funding Opportunity Tracker",
        "subtitle": "Final Year Engineering Project Presentation | React + FastAPI + SQLite",
        "narration": "Respected Guide and Faculty Members, welcome to the presentation of our project: Web Scraping Dashboard and Funding Opportunity Tracker. In this presentation, I will demonstrate how our system automates the tracking of research grants and fellowship deadlines from official portals like BRNS and DST.",
        "bullets": [
            "Project Location: D:\\Project\\Funding Opportunity Web Scraper",
            "Frontend: React 18, TypeScript, Vite, Tailwind CSS (http://localhost:5173)",
            "Backend: Python, FastAPI, Uvicorn, SQLAlchemy (http://127.0.0.1:8000)",
            "Scrapers: BRNS & DST official funding portals"
        ]
    },
    {
        "id": 2,
        "title": "Problem Statement — Manual Portal Checks & Missed Deadlines",
        "subtitle": "Current Challenges Faced by Researchers and Academic Institutions",
        "narration": "Researchers and institutions frequently miss critical research funding opportunities. Government funding agencies like BRNS and DST publish announcements on separate, non-standard websites without active RSS feeds or automatic alert systems. Researchers have to manually check dozens of portals every week.",
        "bullets": [
            "Scattered announcement pages on non-standard websites",
            "Lack of centralized tracking for proposal deadlines",
            "No automatic notification or alert systems on official portals",
            "High risk of missing submission deadlines and funding calls"
        ]
    },
    {
        "id": 3,
        "title": "Proposed Solution — Centralized Monitoring Dashboard",
        "subtitle": "Automated Web Scraping, Structured Parsing & Deadline Tracking",
        "narration": "Our solution is a centralized Web Scraping Dashboard. It automatically scrapes target funding portals, extracts structured opportunity details, parses submission deadlines, links official guideline documents, and computes real-time urgency statuses, all in one unified interface.",
        "bullets": [
            "Centralized web dashboard unifying multi-agency research calls",
            "Automated extraction of grant titles, dates, and document links",
            "Real-time deadline calculation with status indicators",
            "In-website activity notifications and multi-format data exports"
        ]
    },
    {
        "id": 4,
        "title": "System Architecture — Decoupled 3-Tier Data Pipeline",
        "subtitle": "Portals -> BeautifulSoup Scraper -> FastAPI Backend -> SQLite DB -> React UI",
        "narration": "Our system follows a modern decoupled architecture. The scrapers fetch HTML pages from official websites. BeautifulSoup extracts titles, deadlines, schemes, and document links. FastAPI validates and stores data in SQLite using SQLAlchemy ORM. The React frontend fetches data via REST APIs.",
        "bullets": [
            "Scraping Engine: Requests + BeautifulSoup4 HTML parser",
            "Backend Service: FastAPI + Pydantic + SQLAlchemy ORM",
            "Database: SQLite database (data/dashboard.db)",
            "Background Scheduler: APScheduler automated 24-hour cron job"
        ]
    },
    {
        "id": 5,
        "title": "Technology Stack — Modern Full-Stack Tools",
        "subtitle": "Frontend & Backend Framework Rationale",
        "narration": "On the frontend, we use React 18 with TypeScript, Vite, and Tailwind CSS for a fast, responsive user interface. On the backend, we use Python with FastAPI and Uvicorn. SQLite with SQLAlchemy manages database storage, while BeautifulSoup and PyMuPDF handle document parsing.",
        "bullets": [
            "Frontend: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons",
            "Backend API: Python 3.12, FastAPI, Uvicorn, Pydantic",
            "Database & ORM: SQLite, SQLAlchemy ORM",
            "Scraping & Documents: BeautifulSoup4, PyMuPDF, pdfplumber, Pandas"
        ]
    },
    {
        "id": 6,
        "title": "Main Dashboard — Real-Time KPI Cards & Activity Feed",
        "subtitle": "Live Statistics and Real-Time Event Monitoring",
        "narration": "Here is our main Dashboard view. At the top, stat cards display the total tracked portals, total opportunities, active open calls, and urgent grants closing within seven days. On the right, the Activity Panel displays live system updates, such as newly detected opportunities or status changes.",
        "bullets": [
            "Metric Cards: Tracked Portals, Total Opportunities, Open Grants, Closing Soon",
            "Activity Stream: Live audit log of recent scrapes and status updates",
            "Quick Actions: Immediate manual scrape triggering per portal",
            "Responsive Glassmorphism layout built with Tailwind CSS"
        ]
    },
    {
        "id": 7,
        "title": "Funding Opportunities — Search, Filters & Detail Modal",
        "subtitle": "Structured Table with Status Indicators and Document Links",
        "narration": "Under the Opportunities tab, users can view all collected grants in a structured table. Each row displays the Agency Name, Opportunity Title, Category, Announcement Date, Submission Deadline, Document Link, and Status Badge. Users can search by keyword or filter by agency and status.",
        "bullets": [
            "Search & Filter: Filter by status (Open, Closing Soon, Closed) and agency",
            "Opportunity Details: Full description, scheme name, source link",
            "Official Documents: Direct links to official PDF guidelines and forms",
            "Status Badges: Visual color-coded indicators for deadline urgency"
        ]
    },
    {
        "id": 8,
        "title": "BRNS Scraper — Board of Research in Nuclear Sciences",
        "subtitle": "Parsing CRP Calls and PDF Guideline Links from brns.res.in",
        "narration": "Let us examine the BRNS scraper. The official BRNS page lists Call for Coordinated Research Projects. Our specialized BRNS scraper fetches the HTML, extracts the call title, identifies submission deadline dates, resolves relative PDF document links to full URLs, and calculates deadline status.",
        "bullets": [
            "Target URL: https://brns.res.in/content_details.php?content_id=69",
            "Extracted Data: CRP 2026 Phase-I Call, Announcement Date, Submission Deadline",
            "PDF Link Resolution: Converts relative paths to absolute HTTPS document links",
            "Test Verification: Passed 100% fixture and live scraping unit tests"
        ]
    },
    {
        "id": 9,
        "title": "DST Scraper — Department of Science and Technology",
        "subtitle": "Parsing e-PMS Proposals and Guideline Formats from onlinedst.gov.in",
        "narration": "Similarly, the DST scraper targets the e-PMS portal. It parses proposal formats, joint international call announcements, associated department divisions, and application document formats. This demonstrates our scraper architecture's extensibility across multiple government domains.",
        "bullets": [
            "Target URL: https://onlinedst.gov.in/Projectproposalformat.aspx?Id=2232",
            "Extracted Data: Joint Call on IRTG, Division info, application docx link",
            "Duplicate Prevention: Composite key matching on portal ID + title",
            "Extensible Scraper Class: Implements standard BaseScraper interface"
        ]
    },
    {
        "id": 10,
        "title": "Websites & Add URL — Dynamic Portal Management",
        "subtitle": "Registering Target Portals and Automated Validation",
        "narration": "In the Websites view, administrators can monitor tracked source portals, toggle automated scraping, or manually trigger a scrape run. Clicking Add Website allows adding new portals. If an unsupported URL is entered, the system validates the domain, registers it, and marks it for verification.",
        "bullets": [
            "Source Portal Cards: Toggle enabled/disabled status per portal",
            "Add URL Modal: Dynamic portal registration with domain validation",
            "SSRF Protection: Rejects invalid or restricted network address inputs",
            "Manual Execution: Instant 'Scrape Now' button per portal"
        ]
    },
    {
        "id": 11,
        "title": "Scraping History & Automated Background Scheduler",
        "subtitle": "Audit Trails and 24-Hour Recurring Scraping Jobs",
        "narration": "Every scrape execution is recorded in the scrape runs table and visible under Scraping History. This provides auditability by logging start time, completion time, status, duration, items count, and error tracebacks. An APScheduler background job runs automated daily scrapes at midnight.",
        "bullets": [
            "Execution Audit Log: Start time, end time, duration, extracted items count",
            "Status Tracking: Logs Success or Error states with full stack tracebacks",
            "APScheduler Cron Job: Automated 24-hour background scraping",
            "Zero Maintenance: System updates opportunity database automatically"
        ]
    },
    {
        "id": 12,
        "title": "In-Website Notifications — 100% Internal Alert System",
        "subtitle": "Header Notification Drawer & Activity Stream (No External Email)",
        "narration": "Our system features an in-app notification engine. When a new opportunity is discovered or a deadline approaches, an alert is generated and displayed in the Header Notification Bell and Dashboard Activity Panel. The application avoids external email dependencies, keeping all alerts inside the web UI.",
        "bullets": [
            "Notification Bell Drawer: Real-time list of unread system alerts",
            "Activity Stream: Unified dashboard activity event feed",
            "Mark as Read: Interactive notification read state toggling",
            "Zero Email Dependency: 100% in-app UI notifications for maximum privacy"
        ]
    },
    {
        "id": 13,
        "title": "Deadline Monitoring Engine — Timezone & Precedence Matrix",
        "subtitle": "Deterministic Urgency Statuses Evaluated in Asia/Kolkata Timezone",
        "narration": "The deadline engine enforces deterministic status precedence. All dates are evaluated against the Asia/Kolkata timezone. If a date is ambiguous, status is Verification Required. If missing, Unknown. If expired, Closed. If active within seven days, Closing Soon. If valid beyond seven days, Open.",
        "bullets": [
            "Timezone Aware: Evaluated against Asia/Kolkata current local time",
            "Precedence Rules: Verification Required -> Unknown -> Closed -> Upcoming -> Closing Soon -> Open",
            "Official Extension Handling: Preserves original deadline while marking Extended",
            "Tested Logic: 100% passed unit tests covering all status transitions"
        ]
    },
    {
        "id": 14,
        "title": "Reports & Data Export — One-Click Excel & CSV Downloads",
        "subtitle": "Structured Spreadsheet Reports for Institutional Analysis",
        "narration": "For reporting and offline analysis, users can navigate to the Export tab. With a single click, the entire database or filtered records can be downloaded as structured Excel spreadsheets or CSV files, including agency names, titles, deadlines, document links, and direct portal URLs.",
        "bullets": [
            "Export Formats: OpenPyXL Excel (.xlsx) and standard CSV format",
            "Comprehensive Columns: Agency, Title, Category, Dates, Document URLs",
            "Institutional Utility: Ideal for university research office reporting",
            "One-Click Downloads: Direct file streams from FastAPI backend"
        ]
    },
    {
        "id": 15,
        "title": "Database Schema & Security Implementation",
        "subtitle": "Relational Tables, Pydantic Validation & ORM Security",
        "narration": "The SQLite database consists of five normalized tables: websites, opportunities, scrape runs, activities, and opportunity history. For security, FastAPI handles input validation via Pydantic schemas, prevents SQL injection through SQLAlchemy ORM, and enforces URL domain validation.",
        "bullets": [
            "Database Schema: 5 relational tables (websites, opportunities, scrape_runs, etc.)",
            "SQL Injection Prevention: SQLAlchemy ORM parameterized queries",
            "SSRF & URL Security: Strict URL scheme and domain validation",
            "Data Integrity: Foreign key constraints and automated timestamp tracking"
        ]
    },
    {
        "id": 16,
        "title": "Automated Testing & Production Build Verification",
        "subtitle": "17/17 Backend Pytest Passed | 0 Frontend Build Errors",
        "narration": "To guarantee reliability, we developed a pytest test suite covering API endpoints, BRNS and DST scrapers, duplicate detection, and deadline calculation logic. All 17 unit and integration tests pass cleanly. The React production build compiles with zero TypeScript or bundle errors.",
        "bullets": [
            "Backend Pytest Results: 17 passed / 17 total tests (100% pass rate)",
            "Scraper Testing: Verified with fixture HTML and live network responses",
            "Frontend Production Build: Vite compiled 1,366 modules cleanly in 2.91 seconds",
            "Verified Endpoints: /api/health, /api/websites, /api/opportunities, /api/export"
        ]
    },
    {
        "id": 17,
        "title": "Conclusion & Future Enhancements",
        "subtitle": "Automated, Reliable & Scalable Funding Opportunity Tracker",
        "narration": "In conclusion, our Web Scraping Dashboard effectively solves the problem of missed research grants by automating website monitoring, deadline tracking, and document aggregation. Future enhancements include expanding scrapers for SERB and CSIR, NLP eligibility parsing, and RSS feed integration. Thank you!",
        "bullets": [
            "Achieved Objective: Centralized, automated grant tracking system delivered",
            "Immediate Impact: Prevents missed submission deadlines for researchers",
            "Future Roadmap: Expand scrapers to SERB/CSIR, NLP document parsing",
            "Thank You: Open for questions and guide feedback"
        ]
    }
]

def generate_tts_audio(scene_id, text, output_wav):
    """Generates audio narration using gTTS or pyttsx3."""
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        temp_mp3 = output_wav.replace(".wav", ".mp3")
        tts.save(temp_mp3)
        return temp_mp3
    except Exception as e:
        print(f"gTTS failed for Scene {scene_id}, falling back to pyttsx3: {e}")
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.save_to_file(text, output_wav)
        engine.runAndWait()
        return output_wav

def create_slide_image(scene, width=1920, height=1080):
    """Creates a high-resolution dark-themed slide frame using Pillow."""
    img = Image.new('RGB', (width, height), color=(15, 23, 42)) # Slate 900
    draw = ImageDraw.Draw(img)

    # Background gradient effects / accents
    draw.rectangle([0, 0, width, 120], fill=(30, 41, 59)) # Slate 800 Top Bar
    draw.rectangle([0, height-80, width, height], fill=(30, 41, 59)) # Bottom Bar

    # Load fonts (fallback to default if ttf not found)
    try:
        font_title = ImageFont.truetype("arial.ttf", 40)
        font_sub = ImageFont.truetype("arial.ttf", 26)
        font_body = ImageFont.truetype("arial.ttf", 28)
        font_badge = ImageFont.truetype("arial.ttf", 22)
    except:
        font_title = font_sub = font_body = font_badge = ImageFont.load_default()

    # Title & Header
    draw.text((60, 30), f"SCENE {scene['id']}/17  |  {scene['title']}", fill=(56, 189, 248), font=font_title) # Cyan 400
    draw.text((60, 140), scene['subtitle'], fill=(148, 163, 184), font=font_sub) # Slate 400

    # Main Card Box
    draw.rectangle([60, 200, width-60, height-120], fill=(30, 41, 59), outline=(51, 65, 85), width=2)

    # Content Bullets
    y = 240
    for idx, bullet in enumerate(scene['bullets']):
        # Bullet marker
        draw.ellipse([100, y+10, 116, y+26], fill=(56, 189, 248))
        draw.text((140, y), bullet, fill=(241, 245, 249), font=font_body)
        y += 75

    # Bottom bar details
    draw.text((60, height-55), "Web Scraping Dashboard & Funding Opportunity Tracker | College Project Presentation", fill=(148, 163, 184), font=font_badge)
    draw.text((width-320, height-55), "URL: http://localhost:5173", fill=(56, 189, 248), font=font_badge)

    return np.array(img)

def main():
    print("=== Automated Project Video Generator ===")
    print(f"Target Output Directory: {OUTPUT_DIR}")

    srt_entries = []
    current_time_sec = 0.0

    scene_audio_files = []
    scene_durations = []
    slide_images = []

    for idx, scene in enumerate(SCENES):
        print(f"\nProcessing Scene {scene['id']} / {len(SCENES)}: {scene['title']}")

        # 1. Create Audio Narration
        audio_filename = os.path.join(OUTPUT_DIR, f"narration_scene_{scene['id']}.mp3")
        audio_file = generate_tts_audio(scene['id'], scene['narration'], audio_filename)
        scene_audio_files.append(audio_file)

        # Calculate duration based on narration length (approx 2.8 words/sec + 3.0s padding)
        words = len(scene['narration'].split())
        duration = max(18.0, (words / 2.8) + 3.0)
        scene_durations.append(duration)

        # 2. Create Slide Frame Image
        slide_img = create_slide_image(scene)
        slide_images.append(slide_img)

        # 3. Create Subtitle Entry
        start_str = format_srt_time(current_time_sec)
        end_str = format_srt_time(current_time_sec + duration)
        srt_entries.append(f"{scene['id']}\n{start_str} --> {end_str}\n{scene['narration']}\n")
        current_time_sec += duration

    # Write SRT Subtitles File
    with open(SRT_PATH, "w", encoding="utf-8") as f:
        f.writelines("\n".join(srt_entries))
    print(f"\n[OK] Created Subtitles File: {SRT_PATH}")

    # Render Final MP4 Video using imageio
    print(f"\nRendering final MP4 video to {FINAL_MP4_PATH}...")
    fps = 10
    writer = imageio.get_writer(FINAL_MP4_PATH, fps=fps, codec='libx264', pixelformat='yuv420p')

    for idx, (img, dur) in enumerate(zip(slide_images, scene_durations)):
        num_frames = int(dur * fps)
        print(f"Rendering Scene {idx+1}: {num_frames} frames ({dur:.1f}s)...")
        for f_idx in range(num_frames):
            writer.append_data(img)

    writer.close()
    print(f"\n[SUCCESS] Rendered Playable MP4 Video: {FINAL_MP4_PATH}")
    print(f"Total Video Duration: {current_time_sec / 60.0:.2f} minutes")

def format_srt_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

if __name__ == "__main__":
    main()
