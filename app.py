from fastapi import FastAPI, Query
from scrapers.linkedin_jobs import LinkedInJobsScraper
from scrapers.simple_page import SimplePageScraper

app = FastAPI(
    title="Universal Scraper API",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Universal Scraper API"
    }


@app.get("/jobs/linkedin")
async def linkedin_jobs(
    keyword: str = Query(..., description="Suchbegriff, z.B. python"),
    location: str | None = Query(None, description="Ort, z.B. Berlin")
):
    scraper = LinkedInJobsScraper()

    data = await scraper.scrape(
        keyword=keyword,
        location=location
    )

    return {
        "source": "linkedin",
        "keyword": keyword,
        "location": location,
        **data
    }


@app.get("/scrape/simple")
async def simple_scrape(
    url: str = Query(..., description="Ziel-URL"),
    selector: str = Query(..., description="CSS Selector")
):
    scraper = SimplePageScraper()

    results = await scraper.scrape(
        url=url,
        selector=selector
    )

    return {
        "source": url,
        "selector": selector,
        "count": len(results),
        "results": results
    }
