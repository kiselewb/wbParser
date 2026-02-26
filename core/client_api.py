from pathlib import Path

import json

from loguru import logger
from config.paths import COOKIES_FILE
from config.settings import settings
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
            # await self._init_browser()

        logger.info("✅ WB Client Инициализирован")
        logger.debug(self)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.use_session and self.request_api:
            await self.request_api.close_session()

        if self.use_browser:
            pass
            # await self._close_browser()

        logger.info("✅ WB Client закрыт")
        return False

    async def get_products_list(self, page_number: int) -> list:
        url = settings.SEARCH_API_URL
        params = settings.SEARCH_PARAMS.copy()
        params["page"] = page_number

        data = await self.request_api.make_request(self.session, url, params)

        return data.get("products", [])

    # async def _get_product_details(self, product_id: int) -> dict | None:
    #     url = settings.DETAILS_API_URL
    #     params = settings.DETAILS_PARAMS.copy()
    #     params["nm"] = product_id
    #
    #     data = await self._make_request(url, params)
    #
    #     return data.get("products")[0]

    # async def get_product(self, product_id: int) -> tuple[dict, dict, str]:
    #     details = await self._get_product_details(product_id)
    #     card, images_path = await self._get_product_info(product_id)
    #
    #     return details, card, images_path

    @staticmethod
    def _get_cookies() -> dict:
        if not Path(COOKIES_FILE).exists():
            raise CookiesFileNotFoundError()

        with open(COOKIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
