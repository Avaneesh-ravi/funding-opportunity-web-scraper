# GitHub Research Report: BRNS & Government Funding Opportunity Scrapers

## Executive Summary

As part of the **Web Scraping Dashboard — BRNS Funding Opportunity Tracker** project, an extensive code research and dependency audit was performed across GitHub repositories and open-source packages related to `brns.res.in`, Indian government funding portals, and automated funding opportunity scrapers.

---

## 1. Search Queries Executed

1. `brns.res.in scraper`
2. `BRNS funding opportunity scraper`
3. `content_details.php content_id web scraper`
4. `Python government funding website scraper`
5. `grant opportunity scraper Python`
6. `funding deadline extraction GitHub`

---

## 2. Evaluation of Repositories Examined

| Repository / Tool | Primary Focus | License | Relevance & Adaptability | Decision / Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **ericmuckley/foa-finder** | Grants.gov XML database scraper | MIT | Low | Designed specifically for US Grants.gov XML database dumps; incompatible with PHP/HTML tables of Indian research portals. |
| **zaina-saif/GrantAIScraper** | Streamlit + LangChain LLM scraper | Apache 2.0 | Medium | Uses LLM prompting to parse unstructured text. Overkill and expensive for static HTML structures like BRNS content pages. |
| **gefsikatsinelou/MetaSearchMCP** | Grants.gov REST API integration | MIT | Low | Leverages US federal APIs; BRNS has no public REST API available. |
| **CorrelAid/cdl_funding_scraper** | German *Förderdatenbank* HTML scraper | MIT | Medium | Demonstrates HTML parsing with `requests` + `BeautifulSoup4`, but custom selectors are required for BRNS. |
| **zaidejaz/foerderdatenbank-scraper**| Python MySQL database scraper | MIT | Medium | Demonstrates scrape logging patterns; inspiration taken for `scrape_runs` DB schema. |

---

## 3. Key Findings on `brns.res.in`

1. **No Existing BRNS Scraper Found**: A search across public repositories revealed no dedicated scraper for `brns.res.in` or its content portal script `content_details.php`.
2. **Server Characteristics**: `brns.res.in` uses static/server-rendered PHP (`CodeCharge Studio`) outputting HTML elements containing content headers, `Announced on : <date>`, `Last Date of submission: <date>`, and links to PDF announcements (`/public_files/BRNS_Announcement_...pdf`).
3. **API Availability**: No official JSON/REST API exists for BRNS grants.
4. **Conclusion**: A modular custom scraper combining Python `requests`, `BeautifulSoup4`, `pdfplumber`/`PyMuPDF`, and regular expressions provides the most reliable, deterministic, and maintainable solution.

---

## 4. Reusable Architecture Patterns Adopted

From the open-source scrapers evaluated, the following design patterns were adopted into our backend architecture:

- **Abstract Scraper Class (`BaseScraper`)**: Standardized interface returning a unified `ScrapedOpportunity` data class.
- **Scraper Registry (`ScraperManager`)**: Router pattern selecting site-specific scrapers by URL pattern (e.g. matching `brns.res.in`).
- **Scrape Run Auditing**: Execution logging tracking start time, finish time, items found, created, updated, and error messages.
- **SSRF Prevention**: Strict URL validation before dispatching HTTP requests to third-party servers.

---

## 5. Licensing & Safety Compliance

- No proprietary or license-violating code was copied.
- Dependencies utilized (`BeautifulSoup4`, `pdfplumber`, `PyMuPDF`, `FastAPI`, `SQLAlchemy`, `Pydantic`) are standard open-source libraries under permissive MIT/BSD/Apache licenses.
