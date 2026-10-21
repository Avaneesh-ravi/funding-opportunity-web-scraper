import logging
import time
from typing import Optional, Tuple, Dict, Any
from urllib.parse import urlparse, urljoin
import urllib.robotparser
import requests
from requests.exceptions import RequestException

from app.services.security_service import validate_url_security

logger = logging.getLogger(__name__)

# Constants for safe operation
MAX_HTML_SIZE_BYTES = 15 * 1024 * 1024   # 15 MB
MAX_PDF_SIZE_BYTES = 25 * 1024 * 1024    # 25 MB
MAX_REDIRECTS = 5
DEFAULT_CONNECT_TIMEOUT = 10
DEFAULT_READ_TIMEOUT = 20
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36 "
    "(compatible; FundingOpportunityTracker/1.0; +https://funding-opportunity-web-scraper.vercel.app/)"
)


class SafeResponse:
    """Represents a validated, size-bounded HTTP response."""
    def __init__(
        self,
        url: str,
        status_code: int,
        content: bytes,
        headers: Dict[str, str],
        encoding: Optional[str] = None
    ):
        self.url = url
        self.status_code = status_code
        self.content = content
        self.headers = {k.lower(): v for k, v in headers.items()}
        self.encoding = encoding or "utf-8"

    @property
    def text(self) -> str:
        try:
            return self.content.decode(self.encoding, errors="replace")
        except Exception:
            return self.content.decode("utf-8", errors="replace")

    @property
    def content_type(self) -> str:
        return self.headers.get("content-type", "").lower()

    @property
    def is_html(self) -> bool:
        ct = self.content_type
        return "text/html" in ct or "application/xhtml+xml" in ct

    @property
    def is_pdf(self) -> bool:
        ct = self.content_type
        return "application/pdf" in ct or self.url.lower().endswith(".pdf")

    @property
    def is_feed(self) -> bool:
        ct = self.content_type
        return (
            "application/rss+xml" in ct
            or "application/atom+xml" in ct
            or "application/xml" in ct
            or "text/xml" in ct
        )


class SafeHttpClient:
    """
    HTTP client with rigorous SSRF protection on initial request and every redirect hop,
    bounded streaming to prevent decompression bombs, backoff retries, and robots.txt check.
    """

    def __init__(self, user_agent: Optional[str] = None):
        self.user_agent = user_agent or DEFAULT_USER_AGENT
        self.session = requests.Session()
        self._robots_cache: Dict[str, urllib.robotparser.RobotFileParser] = {}

    def is_allowed_by_robots(self, target_url: str) -> bool:
        """
        Inspects the domain's robots.txt to determine if crawling target_url is allowed.
        Falls back to True if robots.txt is 404 or unparseable.
        """
        try:
            parsed = urlparse(target_url)
            base = f"{parsed.scheme}://{parsed.netloc}"
            robots_url = urljoin(base, "/robots.txt")

            if base not in self._robots_cache:
                rp = urllib.robotparser.RobotFileParser()
                rp.set_url(robots_url)
                try:
                    # Validate robots.txt URL security first
                    validate_url_security(robots_url)
                    res = self.session.get(
                        robots_url,
                        headers={"User-Agent": self.user_agent},
                        timeout=(5, 5),
                        allow_redirects=False
                    )
                    if res.status_code == 200:
                        rp.parse(res.text.splitlines())
                    else:
                        # Non-200 means no explicit restrictions
                        rp = None
                except Exception as e:
                    logger.debug("Could not fetch robots.txt for %s: %s", base, e)
                    rp = None
                self._robots_cache[base] = rp

            rp = self._robots_cache.get(base)
            if rp is None:
                return True
            return rp.can_fetch(self.user_agent, target_url)
        except Exception:
            return True

    def fetch(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        max_size: int = MAX_HTML_SIZE_BYTES,
        max_retries: int = 2,
        check_robots: bool = False
    ) -> SafeResponse:
        """
        Safely fetches a URL with SSRF checks on every hop, bounded response size, and retries.
        """
        current_url = url.strip()

        # Initial security check
        validate_url_security(current_url)

        if check_robots and not self.is_allowed_by_robots(current_url):
            logger.warning("URL %s is disallowed by robots.txt; proceeding cautiously.", current_url)

        request_headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf;q=0.8,*/*;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }
        if headers:
            request_headers.update(headers)

        redirect_count = 0
        while redirect_count <= MAX_REDIRECTS:
            # Revalidate security for current redirect URL
            validate_url_security(current_url)

            # Retry loop for transient network/server errors
            for attempt in range(max_retries + 1):
                try:
                    res = self.session.request(
                        method=method,
                        url=current_url,
                        headers=request_headers,
                        timeout=(DEFAULT_CONNECT_TIMEOUT, DEFAULT_READ_TIMEOUT),
                        stream=True,
                        allow_redirects=False
                    )

                    # Check for redirects
                    if res.status_code in (301, 302, 303, 307, 308):
                        location = res.headers.get("Location")
                        if not location:
                            break  # No location header to follow
                        next_url = urljoin(current_url, location)
                        current_url = next_url
                        redirect_count += 1
                        break  # Proceed to next hop in while loop

                    # Handle transient 429 or 5xx with backoff
                    if res.status_code in (429, 502, 503, 504) and attempt < max_retries:
                        backoff = (2 ** attempt) + 0.5
                        logger.info("Received HTTP %d for %s; retrying in %.1fs...", res.status_code, current_url, backoff)
                        time.sleep(backoff)
                        continue

                    # Stream content with size boundary
                    content_length_header = res.headers.get("content-length")
                    if content_length_header and content_length_header.isdigit():
                        if int(content_length_header) > max_size:
                            raise ValueError(
                                f"Response size ({content_length_header} bytes) exceeds limit ({max_size} bytes)"
                            )

                    content_chunks = []
                    bytes_received = 0
                    for chunk in res.iter_content(chunk_size=16384):
                        if chunk:
                            bytes_received += len(chunk)
                            if bytes_received > max_size:
                                raise ValueError(
                                    f"Response stream exceeded maximum size of {max_size} bytes"
                                )
                            content_chunks.append(chunk)

                    raw_content = b"".join(content_chunks)

                    return SafeResponse(
                        url=current_url,
                        status_code=res.status_code,
                        content=raw_content,
                        headers=dict(res.headers),
                        encoding=res.encoding or "utf-8"
                    )

                except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                    if attempt < max_retries:
                        backoff = (2 ** attempt) + 0.5
                        logger.warning("Transient error connecting to %s: %s; retrying in %.1fs...", current_url, e, backoff)
                        time.sleep(backoff)
                    else:
                        raise e

            # If loop finished through redirect, continue while loop
            if redirect_count > MAX_REDIRECTS:
                raise ValueError(f"Exceeded maximum redirect limit of {MAX_REDIRECTS} hops.")

        raise ValueError("Failed to retrieve URL after following redirects.")
