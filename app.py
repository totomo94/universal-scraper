from fastapi import FastAPI, Query
from scrapers.linkedin_jobs import LinkedInJobsScraper
from scrapers.simple_page import SimplePageScraper

app = FastAPI(
    title="Universal Scraper API",
    version="1.2.0"
)


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Universal Scraper API",
        "version": "1.2.0",
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
        description="Maximale Anzahl an Jobseiten, deren Details geöffnet werden. Maximal 50."
    ),
    include_description: bool = Query(
        True,
        description="Wenn true, werden die einzelnen Jobseiten geöffnet und die Stellenbeschreibung extrahiert"
    ),
    time_filter: str | None = Query(
        "r86400",
        description="LinkedIn Zeitfilter. r86400 = letzte 24h, r604800 = letzte Woche, r2592000 = letzter Monat"
    )
):
    scraper = LinkedInJobsScraper()

    data = await scraper.scrape(
        keyword=keyword,
        location=location,
        max_jobs=max_jobs,
        include_description=include_description,
        time_filter=time_filter
    )

    return {
        "source": "linkedin",
        "keyword": keyword,
        "location": location,
        "max_jobs": max_jobs,
        "include_description": include_description,
        "time_filter": time_filter,
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
