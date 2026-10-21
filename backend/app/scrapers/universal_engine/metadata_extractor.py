import json
import logging
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import feedparser

from app.scrapers.universal_engine.date_utils import parse_flexible_date

logger = logging.getLogger(__name__)


def extract_html_metadata(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Extracts Open Graph, Twitter Cards, JSON-LD, and standard HTML meta tags.
    """
    meta_info: Dict[str, Any] = {
        "title": None,
        "description": None,
        "site_name": None,
        "author": None,
        "published_date": None,
        "modified_date": None,
        "json_ld_items": [],
        "feed_urls": []
    }

    if not soup:
        return meta_info

    # 1. Page Title tag
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        meta_info["title"] = title_tag.string.strip()

    # 2. Meta tags
    for tag in soup.find_all("meta"):
        prop = tag.get("property", "").lower()
        name = tag.get("name", "").lower()
        content = tag.get("content", "").strip()

        if not content:
            continue

        # OpenGraph
        if prop == "og:title" and not meta_info["title"]:
            meta_info["title"] = content
        elif prop == "og:description":
            meta_info["description"] = content
        elif prop == "og:site_name":
            meta_info["site_name"] = content
        elif prop in ("article:published_time", "og:published_time"):
            parsed_dt = parse_flexible_date(content)
            if parsed_dt:
                meta_info["published_date"] = parsed_dt
        elif prop in ("article:modified_time", "og:updated_time"):
            parsed_dt = parse_flexible_date(content)
            if parsed_dt:
                meta_info["modified_date"] = parsed_dt

        # Standard meta tags
        if name == "description" and not meta_info["description"]:
            meta_info["description"] = content
        elif name in ("author", "creator") and not meta_info["author"]:
            meta_info["author"] = content
        elif name in ("date", "pubdate", "dc.date"):
            parsed_dt = parse_flexible_date(content)
            if parsed_dt:
                meta_info["published_date"] = parsed_dt

    # 3. JSON-LD Structured Data
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            raw_json = script.string or script.get_text()
            if not raw_json:
                continue
            data = json.loads(raw_json)

            items_to_process = []
            if isinstance(data, list):
                items_to_process.extend(data)
            elif isinstance(data, dict):
                if "@graph" in data and isinstance(data["@graph"], list):
                    items_to_process.extend(data["@graph"])
                else:
                    items_to_process.append(data)

            for item in items_to_process:
                if isinstance(item, dict):
                    meta_info["json_ld_items"].append(item)
                    # Extract dates / sponsor if relevant
                    schema_type = str(item.get("@type", "")).lower()
                    if schema_type in ("grant", "fundingopportunity", "event", "article", "newsarticle", "webpage"):
                        if not meta_info["title"] and item.get("name"):
                            meta_info["title"] = item.get("name")
                        if not meta_info["description"] and item.get("description"):
                            meta_info["description"] = item.get("description")
                        if item.get("startDate") and not meta_info["published_date"]:
                            meta_info["published_date"] = parse_flexible_date(item.get("startDate"))
                        if item.get("validThrough") or item.get("endDate"):
                            meta_info["json_ld_deadline"] = parse_flexible_date(item.get("validThrough") or item.get("endDate"))
                        if item.get("funder"):
                            funder = item.get("funder")
                            if isinstance(funder, dict):
                                meta_info["site_name"] = funder.get("name")
                            elif isinstance(funder, str):
                                meta_info["site_name"] = funder
        except Exception as e:
            logger.debug("Error parsing JSON-LD script: %s", e)

    # 4. Discover linked feeds
    for link in soup.find_all("link", rel=lambda r: r and "alternate" in r):
        link_type = link.get("type", "").lower()
        href = link.get("href")
        if href and ("rss" in link_type or "atom" in link_type or "xml" in link_type):
            meta_info["feed_urls"].append(href)

    return meta_info


def parse_feed_content(feed_content_or_url: str) -> List[Dict[str, Any]]:
    """
    Parses RSS or Atom feed content into a list of normalized entries.
    """
    try:
        parsed_feed = feedparser.parse(feed_content_or_url)
        results = []
        for entry in parsed_feed.entries:
            published_date = None
            if hasattr(entry, "published"):
                published_date = parse_flexible_date(entry.published)
            elif hasattr(entry, "updated"):
                published_date = parse_flexible_date(entry.updated)

            results.append({
                "title": entry.get("title", "").strip(),
                "link": entry.get("link", "").strip(),
                "summary": entry.get("summary", "").strip(),
                "published_date": published_date
            })
        return results
    except Exception as e:
        logger.warning("Error parsing RSS/Atom feed: %s", e)
        return []
