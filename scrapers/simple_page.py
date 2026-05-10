from scrapers.base import BaseScraper
from utils.browser import BrowserManager


class SimplePageScraper(BaseScraper):
    """Generic scraper for extracting text from any URL by CSS selector."""

    async def scrape(self, url: str, selector: str, limit: int = 50):
        async with BrowserManager(headless=True) as page:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(3000)

            items = await page.locator(selector).all_inner_texts()

            return [
                {
                    "text": item.strip(),
                    "source": url,
                    "selector": selector,
                }
                for item in items[:limit]
                if item.strip()
            ]
