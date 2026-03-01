from loguru import logger
from playwright.async_api import async_playwright, Page, Response

from config.settings import settings


class BrowserAPI:
    def __init__(self, headers: dict, cookies: dict):
        self.headers = headers
        self.cookies = cookies
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def open_browser(self) -> Page:
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=settings.HEADLESS_MODE, args=settings.BROWSER_ARGS
        )
        self.context = await self.browser.new_context(**settings.CONTEXT_PARAMS)
        self.context.set_default_timeout(settings.BROWSER_TIMEOUT)
        await self.context.add_cookies(self.cookies)
        await self.context.set_extra_http_headers(self.headers)
        self.page = await self.context.new_page()

        logger.info("✅ Браузер Открыт")

        logger.debug(self.playwright)

        return self.page

    async def close_browser(self):
        await self.page.close()
        await self.context.close()
        await self.browser.close()
        await self.playwright.stop()

        logger.info("✅ Браузер закрыт")

    async def get_product_card(self, product_id: int) -> dict:
        async with self.page.expect_response(
            lambda r: "card.json" in r.url
        ) as response_data:
            await self._open_product_page(product_id)

        response = await response_data.value
        response_data = await response.json()
        response_data["response_url"] = response.url

        return response_data

    async def _open_product_page(self, id: int) -> Response:
        url = settings.SITE_URL + "catalog/" + str(id) + "/detail.aspx"
        logger.debug(f"Используется браузер {self.playwright}")
        return await self.page.goto(url=url, wait_until="domcontentloaded")
