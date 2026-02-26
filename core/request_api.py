import json

from aiohttp import ClientTimeout, ClientSession
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

    @staticmethod
    async def make_request(session: ClientSession, url: str, params: dict | None = None) -> dict | None:
        logger.debug(f"Используется сессия {session}")
        response = await session.get(url=url, params=params)
        response.raise_for_status()
        return json.loads(await response.text())
