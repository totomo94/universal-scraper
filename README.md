# Universal Scraper API

Modularer Playwright-Scraper mit FastAPI, Docker und n8n-kompatibler JSON-Ausgabe.

## Architektur

```text
n8n
 ↓
HTTP Request
 ↓
FastAPI Scraper API
 ↓
Scraper Module
 ↓
JSON zurück an n8n
```

## Projektstruktur

```text
universal-scraper/
├── app.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── scrapers/
│   ├── __init__.py
│   ├── base.py
│   ├── linkedin_jobs.py
│   └── simple_page.py
└── utils/
    ├── __init__.py
    └── browser.py
```

## Lokal mit Docker starten

```bash
docker build -t universal-scraper .
docker run -p 8000:8000 universal-scraper
```

## API testen

### Health Check

```text
http://localhost:8000/health
```

### LinkedIn Jobs

```text
http://localhost:8000/jobs/linkedin?keyword=python&location=Berlin&limit=25
```

### Generischer Webseiten-Scraper

```text
http://localhost:8000/scrape/simple?url=https://example.com&selector=h1
```

## n8n Beispiel

1. Cron Node erstellen
2. HTTP Request Node hinzufügen
3. Methode: GET
4. URL verwenden:

```text
https://deine-domain.de/jobs/linkedin?keyword=python&location=Berlin&limit=25
```

5. Ergebnisse an Telegram, Discord, Google Sheets, Notion oder PostgreSQL weitergeben.

## EasyPanel Deployment

1. Neues Projekt in EasyPanel erstellen
2. Dockerfile-Service auswählen
3. Dieses Projekt hochladen oder Git-Repo verbinden
4. Port `8000` setzen
5. Domain verbinden
6. API über deine Domain aufrufen

## Neuen Scraper hinzufügen

1. Neue Datei in `scrapers/` erstellen, z. B. `my_scraper.py`
2. Von `BaseScraper` erben
3. Methode `scrape()` implementieren
4. In `app.py` neuen Endpoint ergänzen

Beispiel:

```python
from scrapers.base import BaseScraper
from utils.browser import BrowserManager


class MyScraper(BaseScraper):
    async def scrape(self, url: str):
        async with BrowserManager(headless=True) as page:
            await page.goto(url, wait_until="domcontentloaded")
            title = await page.title()
            return {"title": title, "source": url}
```

## Hinweise

LinkedIn kann Rate Limits, Captchas oder IP-Blocks auslösen. Starte mit kleinen Volumen, langsamen Abfragen und sauberem Fehlerhandling.
