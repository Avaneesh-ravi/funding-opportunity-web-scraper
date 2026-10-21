import re
import logging
from typing import List, Set, Tuple
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Keywords indicating a link leads to an individual funding call or announcement
HIGH_VALUE_LINK_PATTERNS = [
    re.compile(r"(?:call[-_ ]?for|proposal|grant|funding|scheme|advertisement|notice|fellowship|announcement|tender|crp)", re.IGNORECASE)
]

# Links to strictly skip
DISQUALIFIED_HREFS = [
    re.compile(r"(?:login|logout|signin|signout|register|signup|cart|checkout|facebook|twitter|instagram|linkedin|youtube|google|javascript:|mailto:|tel:|#)", re.IGNORECASE),
    re.compile(r"\.(?:png|jpg|jpeg|gif|webp|svg|css|js|zip|tar|gz|mp4|mp3|exe)$", re.IGNORECASE)
]


def discover_relevant_links(soup: BeautifulSoup, base_url: str, max_links: int = 5) -> List[Tuple[str, str]]:
    """
    Finds and ranks candidate internal links leading to funding opportunity details.
    Returns list of (normalized_url, link_anchor_text).
    """
    discovered: List[Tuple[str, str]] = []
    seen_urls: Set[str] = {base_url.rstrip("/")}

    try:
        base_host = (urlparse(base_url).hostname or "").lower()
    except Exception:
        return []

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()
        text = a_tag.get_text(" ", strip=True)

        if not href or any(p.search(href) for p in DISQUALIFIED_HREFS):
            continue

        resolved_url = urljoin(base_url, href).split("#")[0].rstrip("/")
        if resolved_url in seen_urls:
            continue

        try:
            parsed_res = urlparse(resolved_url)
            res_host = (parsed_res.hostname or "").lower()
            # Enforce same domain or subdomain constraint
            if not (res_host == base_host or res_host.endswith("." + base_host) or base_host.endswith("." + res_host)):
                continue
            if parsed_res.scheme.lower() not in ("http", "https"):
                continue
        except Exception:
            continue

        # Check relevance in link text or href
        combined_meta = f"{href} {text}".lower()
        is_relevant = any(p.search(combined_meta) for p in HIGH_VALUE_LINK_PATTERNS)

        if is_relevant:
            seen_urls.add(resolved_url)
            discovered.append((resolved_url, text))
            if len(discovered) >= max_links:
                break

    return discovered
