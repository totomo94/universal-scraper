from playwright.async_api import async_playwright


class BrowserManager:
    """Reusable async browser manager for all scraper modules."""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless
        )
        self.page = await self.browser.new_page()
        return self.page

    async def __aexit__(self, exc_type, exc, tb):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
