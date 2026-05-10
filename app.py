from fastapi import FastAPI, Query
from scrapers.linkedin_jobs import LinkedInJobsScraper
from scrapers.simple_page import SimplePageScraper

app = FastAPI(
    title="Universal Scraper API",
    version="1.1.0"
)


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Universal Scraper API",
        "version": "1.1.0",
        "endpoints": [
            "/jobs/linkedin",
            "/scrape/simple"
        ]
    }


@app.get("/jobs/linkedin")
async def linkedin_jobs(
    keyword: str = Query(
        ...,
        description="Suchbegriff, z.B. python, Energietechnik, backend developer"
    ),
    location: str | None = Query(
        None,
        description="Ort, z.B. Berlin, Augsburg oder Remote"
    ),
    max_jobs: int = Query(
        10,
        ge=1,
        le=50,
        description="Maximale Anzahl an Jobseiten, deren Details geöffnet werden"
    ),
    include_description: bool = Query(
        True,
        description="Wenn true, werden die einzelnen Jobseiten geöffnet und die Stellenbeschreibung extrahiert"
    )
):
    scraper = LinkedInJobsScraper()

    data = await scraper.scrape(
        keyword=keyword,
        location=location,
        max_jobs=max_jobs,
        include_description=include_description
    )

    return {
        "source": "linkedin",
        "keyword": keyword,
        "location": location,
        "max_jobs": max_jobs,
        "include_description": include_description,
        **data
    }


@app.get("/scrape/simple")
async def simple_scrape(
    url: str = Query(
        ...,
        description="Ziel-URL"
    ),
    selector: str = Query(
        ...,
        description="CSS Selector, z.B. h1, .title, article"
    )
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
