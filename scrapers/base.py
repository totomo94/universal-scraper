from abc import ABC, abstractmethod


class BaseScraper(ABC):
    """Base class for all scraper modules."""

    @abstractmethod
    async def scrape(self, **kwargs):
        pass
