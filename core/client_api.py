from pathlib import Path

import json

from loguru import logger
from config.paths import COOKIES_FILE
from config.settings import settings
from core.browser_api import BrowserAPI
from core.request_api import RequestAPI
from utils.exceptions import CookiesFileNotFoundError


class ClientAPI:
    def __init__(self, use_session: bool = False, use_browser: bool = False):
        self.use_session = use_session
        self.use_browser = use_browser

        self.headers = settings.HEADERS
        self.cookies = self._get_cookies()

        self.request_api = None
        self.session = None
        self.browser = None

    async def __aenter__(self):
        if self.use_session:
            self.request_api = RequestAPI(self.headers, self.cookies)
            self.session = await self.request_api.get_session()

        if self.use_browser:
            pass
            self.browser_api = BrowserAPI(self.headers, self.cookies)
            self.page = await self.browser_api.open_browser()

        logger.info("✅ WB Client Инициализирован")
        logger.debug(self)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.use_session and self.request_api:
            await self.request_api.close_session()

        if self.use_browser:
            await self.browser_api.close_browser()

        logger.info("✅ WB Client Закрыт")
        return False

    async def get_products_list(self, page_number: int) -> list:
        url = settings.SEARCH_API_URL
        params = settings.SEARCH_PARAMS.copy()
        params["page"] = page_number

        data = await self.request_api.make_request(url, params)

        return data.get("products", [])

    async def get_product_card(self, product_id: int) -> dict:
        data = await self.browser_api.get_product_card(product_id)

        card_data = dict()
        card_data["response_url"] = data.get("response_url", "")
        card_data["media_count"] = data.get("media", {}).get("photo_count", "")
        card_data["options"] = data.get("options", [])
        card_data["description"] = data.get("description", "")

        return card_data

    @staticmethod
    def _get_cookies() -> dict:
        if not Path(COOKIES_FILE).exists():
            raise CookiesFileNotFoundError()

        with open(COOKIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
