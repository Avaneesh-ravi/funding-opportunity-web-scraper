# Production Deployment Guide — Web Scraping Dashboard & Funding Opportunity Tracker

This guide provides step-by-step instructions for deploying the **Web Scraping Dashboard & Funding Opportunity Tracker** to production:
- **Frontend**: [Vercel](https://vercel.com) (React 18 + Vite + TypeScript)
- **Backend**: [Render](https://render.com) (Python 3.12 + FastAPI + Uvicorn)
- **Database**: Persistent SQLite (Render Starter Disk) or Render Managed PostgreSQL

---

## 1. Architecture & Deployment Overview

```
┌─────────────────────────────────┐           ┌──────────────────────────────────────────────┐
│   Vercel (Frontend Hosting)     │           │         Render (Backend Web Service)         │
│   React 18 + TypeScript + Vite  │ ────────> │              FastAPI + Uvicorn               │
│   https://your-app.vercel.app   │  REST API │    https://funding-tracker-api.onrender.com  │
└─────────────────────────────────┘           └──────────────────────┬───────────────────────┘
                                                                     │
                                                    ┌────────────────┴─────────────────┐
                                                    │  Persistent SQLite / PostgreSQL  │
                                                    │  /opt/render/project/data/*.db   │
                                                    └──────────────────────────────────┘
```

---

## 2. Prerequisites

1. A **GitHub** account (to host the repository).
2. A **Render** account ([https://render.com](https://render.com)).
3. A **Vercel** account ([https://vercel.com](https://vercel.com)).

---

## 3. Step 1: Push Code to GitHub

Open PowerShell or Command Prompt in the project directory:

```bash
cd "D:\Project\Funding Opportunity Web Scraper"

# Initialize Git repository (if not already done)
git init

# Verify .gitignore is in place (ensures venv, node_modules, and .env are not committed)
git status

# Stage all project files
git add .

# Create initial commit
git commit -m "feat: production deployment configuration for Vercel and Render"

# Add your GitHub remote repository (replace with your repo URL)
git branch -M main
git remote add origin https://github.com/your-username/funding-opportunity-tracker.git
git push -u origin main
```

---

## 4. Step 2: Deploy Backend on Render

### Method A: Manual Web Service Setup (Recommended)

1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** > **Web Service**.
3. Connect your GitHub repository (`funding-opportunity-tracker`).
4. Configure the Web Service settings:
   - **Name**: `funding-tracker-api`
   - **Region**: Choose the region closest to you (e.g., `Singapore` or `Frankfurt`).
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. **Configure Persistent Disk (for SQLite)**:
   > **Note on Storage Options**:
   > - **Option 1 (SQLite with Persistent Disk)**: On Render's **Starter** plan ($7/mo), go to the **Disks** section in the service settings, click **Add Disk**:
   >   - **Name**: `sqlite-data`
   >   - **Mount Path**: `/opt/render/project/data`
   >   - **Size**: `1 GB`
   >   Set `DATABASE_URL` to: `sqlite:////opt/render/project/data/dashboard.db`
   > - **Option 2 (Free PostgreSQL)**: If using Render's **Free** tier (disks unavailable on free web services), create a **PostgreSQL** database in Render (Free tier), copy the Internal Database URL, and set `DATABASE_URL` to that value. The backend code automatically handles `postgresql://` connections!

6. **Add Environment Variables**:
   Under **Environment Variables**, add:
   | Key | Value | Purpose |
   | :--- | :--- | :--- |
   | `PYTHON_VERSION` | `3.12.0` | Python runtime version |
   | `DEBUG` | `false` | Production mode (disables debug reload) |
   | `DATABASE_URL` | `sqlite:////opt/render/project/data/dashboard.db` | Path to persistent database |
   | `CORS_ORIGINS_STR` | `http://localhost:5173` | Allowed origins (update with Vercel URL later) |
   | `TIMEZONE` | `Asia/Kolkata` | Application timezone for deadline checks |
   | `SCRAPER_TIMEOUT` | `30` | Outbound scraper HTTP timeout |

7. Click **Create Web Service**. Wait for the build and deployment to complete.
8. Note your Render URL (e.g., `https://funding-tracker-api.onrender.com`).

### Verify Backend Health
Open in your browser:
```
https://funding-tracker-api.onrender.com/api/health
```
Expected response:
```json
{
  "status": "healthy",
  "app_name": "Web Scraping Dashboard — BRNS Funding Opportunity Tracker",
  "timezone": "Asia/Kolkata",
  "debug": false,
  "scheduler_running": true,
  "cors_origins": ["http://localhost:5173"]
}
```

---

## 5. Step 3: Deploy Frontend on Vercel

1. Log in to [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **Add New...** > **Project**.
3. Import your GitHub repository (`funding-opportunity-tracker`).
4. In the **Configure Project** screen:
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click Edit, select `frontend`, and click Continue.
   - **Build Command**: `npm run build` (Default)
   - **Output Directory**: `dist` (Default)
   - **Install Command**: `npm install` (Default)

5. **Add Environment Variable**:
   Under **Environment Variables**, add:
   | Name | Value |
   | :--- | :--- |
   | `VITE_API_BASE_URL` | `https://funding-tracker-api.onrender.com` |

   *(Replace with your actual Render backend URL, without a trailing slash).*

6. Click **Deploy**. Vercel will install dependencies, build the production bundle, and assign a production URL (e.g., `https://funding-tracker.vercel.app`).

---

## 6. Step 4: Link Frontend and Backend (Configure CORS)

Now that you have your production Vercel URL, update Render's allowed CORS origins:

1. Go to your **Render Dashboard** > Select `funding-tracker-api`.
2. Go to **Environment** tab.
3. Update `CORS_ORIGINS_STR`:
   ```env
   CORS_ORIGINS_STR=https://funding-tracker.vercel.app,http://localhost:5173
   ```
   *(Include your exact Vercel URL and local development URL separated by a comma).*
4. Click **Save Changes**. Render will automatically redeploy with the updated CORS policy.

---

## 7. Post-Deployment Verification Checklist

Verify each feature on your live Vercel application:

- [ ] **Health Endpoint**: `https://your-backend.onrender.com/api/health` returns `healthy` and `scheduler_running: true`.
- [ ] **Swagger Documentation**: `https://your-backend.onrender.com/docs` opens the interactive API docs.
- [ ] **Dashboard Loading**: Opening `https://your-frontend.vercel.app` loads KPI metric cards and activity stream.
- [ ] **SPA Direct Navigation**: Refreshing the browser on `/opportunities`, `/websites`, or `/history` works without 404 errors (verified via `vercel.json`).
- [ ] **Live BRNS Scrape**: On the Websites page, click **Scrape Now** on the BRNS row; verify opportunities and activity feed update.
- [ ] **Live DST Scrape**: Click **Scrape Now** on the DST row; verify the e-PMS opportunity and scheme information appear.
- [ ] **Add URL Validation**: Click **Add Website** and test:
  - Entering `http://127.0.0.1:8000/` or `http://localhost` is blocked with a 400 SSRF security message.
  - Entering an unsupported public website registers it and correctly displays `Scraper not configured` without crashing.
- [ ] **Opportunity Filtering & Details**: Use the search bar, agency filter, and status dropdowns. Click an opportunity to open the detail modal and verify PDF links.
- [ ] **In-App Notifications**: Click the header bell icon to inspect the notification drawer and test **Mark All as Read**.
- [ ] **Data Export**: On the Export tab, click **Download CSV** and **Download Excel (.xlsx)**; verify downloaded files open with complete opportunity columns.

---

## 8. Background Scheduler & Worker Notes

- **Single Web Instance (Default)**: The background scheduler (`APScheduler`) runs inside the FastAPI process. On Render's single-instance deployment, it runs a daily cron job at midnight (`00:00 Asia/Kolkata`) without duplicate jobs.
- **Scaling to Multiple Workers**: If you scale Uvicorn to multiple workers (`--workers N > 1`), move the scheduler to a dedicated Render Background Worker service that runs `python -m app.worker` to prevent duplicate daily scraping executions.
- **Zero Email Dependency**: The system operates 100% with in-app notifications and database activity logs. No SMTP or email configuration is required.
