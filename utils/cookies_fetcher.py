import asyncio
import json

from loguru import logger
from playwright.async_api import async_playwright, Cookie, Error

from config.paths import COOKIES_DIR, COOKIES_FILE
from config.settings import settings
from utils.logger import setup_logger


class CookiesManager:
    def __init__(self):
        self._create_cookies_dir()
        setup_logger()

    async def write_cookies(self):
        cookies = await self._get_cookies()
        with open(COOKIES_FILE, "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=4, ensure_ascii=False)

    @staticmethod
    async def _get_cookies() -> list[Cookie] | None:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=settings.HEADLESS_MODE, args=settings.BROWSER_ARGS
            )

            context = await browser.new_context(**settings.CONTEXT_PARAMS)
            context.set_default_timeout(settings.BROWSER_TIMEOUT)
            page = await context.new_page()

            try:
                await page.goto(settings.SITE_URL, wait_until="domcontentloaded")
                await page.wait_for_selector(".main-page")

                page_cookies = await page.context.cookies(settings.SITE_URL)

                logger.info("✅ Cookies успешно получены")

                return page_cookies

            except Error as e:
                logger.error(f"❌ Ошибка получения Cookies:\n {e.message}")
                return None

            finally:
                await browser.close()

    @staticmethod
    def _create_cookies_dir():
        COOKIES_DIR.mkdir(parents=True, exist_ok=True)


cookies_manager = CookiesManager()
asyncio.run(cookies_manager.write_cookies())
