from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # SEARCH SETTINGS
    SITE_URL: str
    SEARCH_API_URL: str
    DETAILS_API_URL: str

    SEARCH_QUERY: str
    DEST: str
    LIMIT: str

    @property
    def SEARCH_PARAMS(self) -> dict:
        return {
            "dest": self.DEST,
            "resultset": "catalog",
            "query": self.SEARCH_QUERY,
            "sort": "popular",
            "limit": self.LIMIT,
        }

    @property
    def DETAILS_PARAMS(self) -> dict:
        return {"dest": self.DEST}

    # BROWSER SETTINGS
    HEADLESS_MODE: bool
    BROWSER_TIMEOUT: int

    # REQUESTS SETTINGS
    REQUEST_TIMEOUT: int

    # BROWSER CONFIG
    BROWSER_ARGS: list = [
        "--disable-blink-features=AutomationControlled",
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--lang=ru-RU",
    ]
    CONTEXT_PARAMS: dict = {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "extra_http_headers": {
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
            "Sec-ch-ua-mobile": "?0",
            "Sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
        },
    }
    HEADERS: dict = {
        "User-Agent": CONTEXT_PARAMS.get("user_agent"),
        "Accept-Language": CONTEXT_PARAMS.get("extra_http_headers").get(
            "Accept-Language"
        ),
    }

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class LogsSettings(BaseSettings):
    IS_FILE_LOG: bool
    IS_CONSOLE_LOG: bool
    LOG_LEVEL: str
    LOG_ROTATION: str
    LOG_COMPRESSION: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class ReportSettings(BaseSettings):
    HEADERS: list[str] = [
        "Ссылка на товар",
        "Артикул",
        "Название",
        "Цена",
        "Описание",
        "Изображения",
        "Характеристики",
        "Продавец",
        "Ссылка на продавца",
        "Размеры",
        "Остаток товара",
        "Рейтинг",
        "Количество отзывов",
    ]


settings = Settings()
logs_settings = LogsSettings()
report_settings = ReportSettings()
