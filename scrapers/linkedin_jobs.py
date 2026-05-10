from urllib.parse import urlencode

from scrapers.base import BaseScraper
from utils.browser import BrowserManager


class LinkedInJobsScraper(BaseScraper):
    """Scrapes public LinkedIn job search result cards."""

    async def scrape(self, keyword: str, location: str | None = None, limit: int = 25):
        params = {
            "keywords": keyword,
        }

        if location:
            params["location"] = location

        url = "https://www.linkedin.com/jobs/search/?" + urlencode(params)

        async with BrowserManager(headless=True) as page:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(5000)

            titles = await page.locator(".job-search-card__title").all_inner_texts()
            companies = await page.locator(".job-search-card__subtitle").all_inner_texts()
            locations = await page.locator(".job-search-card__location").all_inner_texts()
            links = await page.locator(".base-card__full-link").evaluate_all(
                "elements => elements.map(el => el.href)"
            )

            jobs = []
            max_items = min(len(titles), len(companies), len(locations), len(links), limit)

            for i in range(max_items):
                jobs.append({
                    "title": titles[i].strip(),
                    "company": companies[i].strip(),
                    "location": locations[i].strip(),
                    "url": links[i],
                    "source": "linkedin",
                })

            return jobs
