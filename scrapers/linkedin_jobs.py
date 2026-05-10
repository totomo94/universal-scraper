from urllib.parse import urlencode
from scrapers.base import BaseScraper
from utils.browser import BrowserManager


class LinkedInJobsScraper(BaseScraper):
    async def scrape(self, keyword: str, location: str | None = None):
        async with BrowserManager(headless=True) as page:
            params = {
                "keywords": keyword
            }

            if location:
                params["location"] = location

            url = "https://www.linkedin.com/jobs/search/?" + urlencode(params)

            await page.set_extra_http_headers({
                "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
            })

            await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            await page.wait_for_timeout(8000)

            page_title = await page.title()
            current_url = page.url
            body_text = await page.locator("body").inner_text(timeout=10000)

            # Debug-Hinweise erkennen
            lower_body = body_text.lower()

            blocked_indicators = [
                "captcha",
                "security verification",
                "unusual activity",
                "sign in",
                "join linkedin",
                "authwall",
                "challenge"
            ]

            detected_blocks = [
                indicator
                for indicator in blocked_indicators
                if indicator in lower_body
            ]

            # Mehrere mögliche Selektoren testen
            selectors = [
                ".job-search-card",
                ".base-card",
                "li[data-occludable-job-id]",
                ".jobs-search__results-list li"
            ]

            cards = None
            used_selector = None

            for selector in selectors:
                count = await page.locator(selector).count()

                if count > 0:
                    cards = page.locator(selector)
                    used_selector = selector
                    break

            if not cards:
                await page.screenshot(path="linkedin-debug-no-results.png", full_page=True)

                html = await page.content()

                return {
                    "debug": True,
                    "url": url,
                    "current_url": current_url,
                    "page_title": page_title,
                    "used_selector": None,
                    "detected_blocks": detected_blocks,
                    "body_preview": body_text[:1500],
                    "html_preview": html[:1500],
                    "results": []
                }

            jobs = []
            count = await cards.count()

            for i in range(min(count, 25)):
                card = cards.nth(i)

                title = await self.safe_text(card, [
                    ".job-search-card__title",
                    ".base-search-card__title",
                    "h3",
                    "a"
                ])

                company = await self.safe_text(card, [
                    ".job-search-card__subtitle",
                    ".base-search-card__subtitle",
                    "h4"
                ])

                job_location = await self.safe_text(card, [
                    ".job-search-card__location",
                    ".job-search-card__metadata",
                    ".base-search-card__metadata"
                ])

                link = await self.safe_attr(card, [
                    ".base-card__full-link",
                    "a"
                ], "href")

                if title:
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": job_location,
                        "url": link,
                        "source": "linkedin"
                    })

            return {
                "debug": False,
                "url": url,
                "current_url": current_url,
                "page_title": page_title,
                "used_selector": used_selector,
                "detected_blocks": detected_blocks,
                "count": len(jobs),
                "results": jobs
            }

    async def safe_text(self, parent, selectors):
        for selector in selectors:
            try:
                locator = parent.locator(selector).first()

                if await locator.count() > 0:
                    text = await locator.inner_text(timeout=3000)

                    if text:
                        return text.strip()
            except Exception:
                continue

        return ""

    async def safe_attr(self, parent, selectors, attr):
        for selector in selectors:
            try:
                locator = parent.locator(selector).first()

                if await locator.count() > 0:
                    value = await locator.get_attribute(attr, timeout=3000)

                    if value:
                        return value.strip()
            except Exception:
                continue

        return ""
