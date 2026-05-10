from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from scrapers.linkedin_jobs import LinkedInJobsScraper
from scrapers.simple_page import SimplePageScraper

app = FastAPI(
    title="Universal Scraper API",
    version="1.0.0",
    description="Modular Playwright scraper API for n8n, Docker and EasyPanel."
)


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Universal Scraper API",
        "endpoints": [
            "/jobs/linkedin?keyword=python&location=Berlin",
            "/scrape/simple?url=https://example.com&selector=h1",
        ],
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/jobs/linkedin")
async def linkedin_jobs(
    keyword: str = Query(..., description="Search keyword, e.g. python"),
    location: str | None = Query(None, description="Optional location, e.g. Berlin"),
    limit: int = Query(25, ge=1, le=100, description="Maximum number of jobs")
):
    try:
        scraper = LinkedInJobsScraper()
        results = await scraper.scrape(
            keyword=keyword,
            location=location,
            limit=limit,
        )

        return {
            "source": "linkedin",
            "keyword": keyword,
            "location": location,
            "count": len(results),
            "results": results,
        }
    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={
                "source": "linkedin",
                "keyword": keyword,
                "location": location,
                "error": str(error),
            },
        )


@app.get("/scrape/simple")
async def simple_scrape(
    url: str = Query(..., description="Target URL"),
    selector: str = Query(..., description="CSS selector, e.g. h1, .title, article h2"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results")
):
    try:
        scraper = SimplePageScraper()
        results = await scraper.scrape(
            url=url,
            selector=selector,
            limit=limit,
        )

        return {
            "source": url,
            "selector": selector,
            "count": len(results),
            "results": results,
        }
    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={
                "source": url,
                "selector": selector,
                "error": str(error),
            },
        )
