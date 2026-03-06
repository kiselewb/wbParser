import asyncio

from loguru import logger
from playwright.async_api import async_playwright, Page, Response, Error, TimeoutError

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
        for obj, name in [
            (self.page, "page"),
            (self.context, "context"),
            (self.browser, "browser"),
        ]:
            if obj:
                try:
                    await obj.close()
                except Error as e:
                    logger.warning(f"⚠️ Ошибка при закрытии {name}: {e.message}")

        if self.playwright:
            try:
                await self.playwright.stop()
            except Error as e:
                logger.warning(f"⚠️ Ошибка при остановке playwright: {e.message}")

        logger.info("✅ Браузер закрыт")

    async def get_product_card(self, product_id: int, retries: int = 3) -> dict | None:
        for attempt in range(retries):
            try:
                async with self.page.expect_response(
                        lambda r: "card.json" in r.url
                ) as response_info:
                    await self._open_product_page(product_id)

                response = await response_info.value
                data = await response.json()
                data["response_url"] = response.url
                return data

            except TimeoutError as e:
                wait = 2 ** attempt
                logger.warning(
                    f"⚠️ Ошибка при получении карточки товара {product_id}: {e}. "
                    f"Повтор через {wait}с (попытка {attempt + 1}/{retries})"
                )
                await asyncio.sleep(wait)

            except Exception as e:
                logger.error(f"❌ Ошибка при получении карточки товара {product_id}: {e}")
                return None

        logger.error(f"❌ Все {retries} попытки исчерпаны: {product_id}")
        return None

    async def _open_product_page(self, id: int) -> Response:
        url = settings.SITE_URL + "catalog/" + str(id) + "/detail.aspx"
        logger.debug(f"Используется браузер {self.playwright}")
        return await self.page.goto(url=url, wait_until="domcontentloaded")
