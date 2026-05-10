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
                "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
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

            lower_body = body_text.lower()

            blocked_indicators = [
                "captcha",
                "security verification",
                "unusual activity",
                "sign in",
                "join linkedin",
                "authwall",
                "challenge",
                "sicherheitsüberprüfung",
                "einloggen",
                "anmelden"
            ]

            detected_blocks = [
                indicator
                for indicator in blocked_indicators
                if indicator in lower_body
            ]

            # Erst normale Job-Karten suchen
            selectors = [
                ".job-search-card",
                ".base-search-card",
                ".base-card",
                "li[data-occludable-job-id]",
                ".jobs-search__results-list li"
            ]

            used_selector = None
            card_count = 0

            for selector in selectors:
                count = await page.locator(selector).count()

                if count > 0:
                    used_selector = selector
                    card_count = count
                    break

            if not used_selector:
                await page.screenshot(
                    path="linkedin-debug-no-cards.png",
                    full_page=True
                )

                html = await page.content()

                return {
                    "debug": True,
                    "url": url,
                    "current_url": current_url,
                    "page_title": page_title,
                    "used_selector": None,
                    "card_count": 0,
                    "detected_blocks": detected_blocks,
                    "body_preview": body_text[:2000],
                    "html_preview": html[:2000],
                    "count": 0,
                    "results": []
                }

            # Robuste Extraktion direkt im Browser-Kontext
            jobs = await page.locator(used_selector).evaluate_all(
                """
                (cards) => {
                    return cards.map((card) => {
                        const pickText = (selectors) => {
                            for (const selector of selectors) {
                                const el = card.querySelector(selector);
                                if (el && el.innerText && el.innerText.trim()) {
                                    return el.innerText.trim();
                                }
                                if (el && el.textContent && el.textContent.trim()) {
                                    return el.textContent.trim();
                                }
                            }
                            return "";
                        };

                        const pickAttr = (selectors, attr) => {
                            for (const selector of selectors) {
                                const el = card.querySelector(selector);
                                if (el && el.getAttribute(attr)) {
                                    return el.getAttribute(attr);
                                }
                            }
                            return "";
                        };

                        const title = pickText([
                            ".base-search-card__title",
                            ".job-search-card__title",
                            "h3",
                            "a"
                        ]);

                        const company = pickText([
                            ".base-search-card__subtitle",
                            ".job-search-card__subtitle",
                            "h4",
                            ".hidden-nested-link"
                        ]);

                        const location = pickText([
                            ".job-search-card__location",
                            ".base-search-card__metadata",
                            ".job-search-card__metadata",
                            ".job-search-card__listdate",
                            ".job-search-card__benefits"
                        ]);

                        let link = pickAttr([
                            ".base-card__full-link",
                            "a[href*='/jobs/view']",
                            "a"
                        ], "href");

                        if (link && link.startsWith("/")) {
                            link = "https://www.linkedin.com" + link;
                        }

                        return {
                            title,
                            company,
                            location,
                            url: link,
                            source: "linkedin",
                            raw_text: card.innerText ? card.innerText.trim() : ""
                        };
                    });
                }
                """
            )

            # Fallback: Wenn Titel leer ist, aus raw_text die ersten Zeilen ableiten
            cleaned_jobs = []

            for job in jobs:
                title = job.get("title", "").strip()
                company = job.get("company", "").strip()
                job_location = job.get("location", "").strip()
                link = job.get("url", "").strip()
                raw_text = job.get("raw_text", "").strip()

                if not title and raw_text:
                    lines = [
                        line.strip()
                        for line in raw_text.split("\n")
                        if line.strip()
                    ]

                    if len(lines) > 0:
                        title = lines[0]

                    if len(lines) > 1 and not company:
                        company = lines[1]

                    if len(lines) > 2 and not job_location:
                        job_location = lines[2]

                # Nur Jobs behalten, die wenigstens Titel oder Link haben
                if title or link:
                    cleaned_jobs.append({
                        "title": title,
                        "company": company,
                        "location": job_location,
                        "url": link,
                        "source": "linkedin"
                    })

            await page.screenshot(
                path="linkedin-debug-success.png",
                full_page=True
            )

            return {
                "debug": False,
                "url": url,
                "current_url": current_url,
                "page_title": page_title,
                "used_selector": used_selector,
                "card_count": card_count,
                "detected_blocks": detected_blocks,
                "count": len(cleaned_jobs),
                "results": cleaned_jobs[:25]
            }
