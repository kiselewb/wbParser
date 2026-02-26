import json

from core.client_api import ClientAPI
from config.paths import DATA_DIR, PRODUCTS_ID_FILE
from utils.exceptions import ProductsIDsNotFoundError
from loguru import logger


class IdProductCollector:
    def __init__(self, client: ClientAPI):
        self.client = client
        self._create_products_id_file()

    async def collect_ids(self):
        await self._get_ids()

    async def _get_ids(self) -> bool | None:
        logger.info("📊 Начало получения списка ID товаров")

        products_ids_len = 0
        current_page = 1

        while True:
            products_list = await self.client.get_products_list(current_page)

            if not products_list:
                break

            temp_ids_list = [product.get("id", "x000x") for product in products_list]

            self._save_ids(temp_ids_list)
            products_ids_len += len(temp_ids_list)

            current_page += 1

        if products_ids_len:
            logger.info(
                f"✅ Список ID товаров успешно получен. Всего товаров: {products_ids_len}"
            )
            return True
        else:
            raise ProductsIDsNotFoundError()

    @staticmethod
    def _save_ids(new_data: list):
        with open(PRODUCTS_ID_FILE, "r+", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []

            data.extend(new_data)

            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.truncate()

    @staticmethod
    def _create_products_id_file():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(PRODUCTS_ID_FILE, "w", encoding="utf-8"):
            pass
