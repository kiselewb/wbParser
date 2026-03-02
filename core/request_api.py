import asyncio
import json

from aiohttp import ClientTimeout, ClientSession, ClientResponseError
from loguru import logger
from config.settings import settings


class RequestAPI:
    def __init__(self, headers: dict, cookies: dict):
        self.headers = headers
        self.cookies = cookies
        self.session = None

    async def get_session(self) -> ClientSession:
        for cookie in self.cookies:
            if cookie.get("name", "") == "x_wbaas_token":
                self.headers["X-Wbaas-Token"] = cookie["value"]

        self.session = ClientSession(
            headers=self.headers,
            raise_for_status=True,
            timeout=ClientTimeout(settings.REQUEST_TIMEOUT),
        )

        logger.info("✅ HTTP Сессия Открыта")
        logger.debug(self.session)

        return self.session

    async def close_session(self) -> None:
        await self.session.close()
        logger.info("✅ HTTP Сессия Закрыта")

    async def make_request(self, url: str, params: dict | None = None, retries: int = 3) -> dict | None:
        for attempt in range(retries):
            try:
                logger.debug(f"Используется сессия {self.session}")
                response = await self.session.get(url=url, params=params)
                response.raise_for_status()
                return json.loads(await response.text())
            except ClientResponseError as e:
                if e.status == 429:
                    wait = 2 ** attempt
                    logger.warning(f"⚠️ 429 Too Many Requests. Повтор через {wait}с (попытка {attempt + 1}/{retries})")
                    await asyncio.sleep(wait)
                else:
                    logger.error(f"❌ HTTP ошибка {e.status}: {url}")
                    return None
            except Exception as e:
                logger.error(f"❌ Неожиданная ошибка запроса: {e}")
                return None

        logger.error(f"❌ Все {retries} попытки исчерпаны: {url}")
        return None
