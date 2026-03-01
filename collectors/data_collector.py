import json
from typing import AsyncGenerator, Any

from config.paths import PRODUCTS_FILE, DATA_DIR, PRODUCTS_ID_FILE
from config.settings import settings
from core.client_api import ClientAPI
from loguru import logger


class DataProductCollector:
    def __init__(self, client: ClientAPI):
        self.client = client
        self._create_products_data_file()

    async def collect_data(self, is_from_file: bool = False) -> None:
        if is_from_file:
            async for id in self._products_ids_generator():
                await self.parse_product(id)
        else:
            async for product in self.parse_products():
                self._save_product(product)

    async def parse_products(self) -> AsyncGenerator[dict]:
        async for product, index in self._products_generator():
            logger.info(f"📍 {index}: парсинг {product.get('id')}")

            card = await self.client.get_product_card(product.get("id"))

            details = self._parse_details(product)
            info = self._get_info(card)
            images = self._parse_images(card)

            yield details | info | images

    async def parse_product(self, product_id: int) -> dict:
        logger.info(f"📍 Единичный парсинг {product_id}")

        product = await self.client.get_product(product_id)
        card = await self.client.get_product_card(product_id)

        details = self._parse_details(product)
        info = self._get_info(card)
        images = self._parse_images(card)

        return details | info | images

    def _parse_details(self, data: dict) -> dict:
        return {
            "link": f"{settings.SITE_URL}catalog/{data.get('id')}/detail.aspx",
            "product_id": data.get("id", "NO_DATA"),
            "title": data.get("name", "NO_DATA"),
            "price": self._get_price(data),
            "seller_name": data.get("supplier", "NO_DATA"),
            "seller_link": (
                f"{settings.SITE_URL}seller/{data['supplierId']}"
                if data.get("supplierId")
                else "NO_DATA"
            ),
            "sizes": ", ".join(size["name"] for size in data.get("sizes", []))
            or "NO_DATA",
            "quantity": data.get("totalQuantity", "NO_DATA"),
            "rating": data.get("reviewRating", "NO_DATA"),
            "reviews_count": data.get("feedbacks", "NO_DATA"),
        }

    @staticmethod
    def _get_price(data: dict) -> int | str:
        for size in data.get("sizes", []):
            price = size.get("price", {})
            if "product" in price:
                return price["product"]
        return "NO_DATA"

    @staticmethod
    def _get_info(data: dict) -> dict:
        description = data.get("description", "NO_DATA")

        options_data = data.get("options", [])
        options = (
            [
                {"name": option["name"], "value": option["value"]}
                for option in options_data
            ]
            if options_data
            else "NO_DATA"
        )

        return {
            "description": description,
            "options": options,
        }

    @staticmethod
    def _parse_images(data: dict) -> dict:
        images_path = data.get("response_url", "")
        images_count = data.get("media_count", 0)

        if images_count and images_path:
            path = images_path.replace("info/ru/card.json", "images/big/")
            images = [f"{path}{index}.webp" for index in range(1, images_count + 1)]
            return {"images": images}
        return {"images": []}

    async def _products_generator(self) -> AsyncGenerator[tuple[Any, int], Any]:
        logger.info("📊 Начало получения списка товаров")

        total = 0
        page = 4
        while True:
            products_list = await self.client.get_products_list(page)
            if not products_list:
                break
            for product in products_list:
                total += 1
                yield product, total
            page += 1

        if not total:
            logger.error("❌ ID товаров не найдены. Работа программы остановлена")
            return

        logger.info(f"✅ Товары успешно найдены и обработаны. Всего товаров: {total}")

    @staticmethod
    async def _products_ids_generator() -> AsyncGenerator[int]:
        with open(PRODUCTS_ID_FILE, "r", encoding="utf-8") as f:
            ids = json.load(f)

        logger.info(f"Из файла загружено {len(ids)} ID товаров")

        for id in ids:
            logger.debug(id)
            yield id

    @staticmethod
    def _save_product(data: dict) -> None:
        with open(PRODUCTS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

    @staticmethod
    def _create_products_data_file() -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(PRODUCTS_FILE, "w", encoding="utf-8"):
            pass
