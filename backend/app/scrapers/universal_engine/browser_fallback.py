import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def is_spa_shell(html: str, body_text_len: int) -> bool:
    """
    Detects if an HTML page appears to be an unrendered Single Page Application shell.
    """
    if not html:
        return True

    lower_html = html.lower()
    has_empty_root = (
        '<div id="root"></div>' in lower_html
        or '<div id="app"></div>' in lower_html
        or '<div id="__next"></div>' in lower_html
        or '<div id="root"> </div>' in lower_html
    )

    # If it has an empty mount root or very short content with multiple script tags
    if has_empty_root and body_text_len < 250:
        return True

    if body_text_len < 100 and "<script" in lower_html:
        return True

    return False


def render_with_browser_if_available(url: str, timeout_sec: int = 15) -> Tuple[Optional[str], Optional[str]]:
    """
    Attempts to render a client-side JavaScript page using Playwright if installed.
    Returns (rendered_html, diagnostic_note).
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        note = "JavaScript-rendered page detected. Headless browser runtime (Playwright) is not installed in environment; using static extraction."
        logger.info(note)
        return (None, note)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            page = browser.new_page()
            page.set_default_timeout(timeout_sec * 1000)
            page.goto(url, wait_until="domcontentloaded")
            # Wait briefly for dynamic content to hydrate
            page.wait_for_timeout(2000)
            rendered_content = page.content()
            browser.close()
            return (rendered_content, "Rendered successfully via headless browser.")
    except Exception as e:
        note = f"Browser rendering attempt failed: {str(e)}"
        logger.warning("Browser rendering failed for %s: %s", url, e)
        return (None, note)
