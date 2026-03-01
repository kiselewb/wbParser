import asyncio

from asyncio import CancelledError

from loguru import logger

from collectors.data_collector import DataProductCollector
from core.client_api import ClientAPI
from collectors.id_collector import IdProductCollector
from utils.exceptions import ParserException
from utils.logger import setup_logger


async def main():
    setup_logger()

    try:
        async with ClientAPI(True, True) as client:
            # id_collector = IdProductCollector(client)
            # await id_collector.collect_ids()

            data_collector = DataProductCollector(client)
            await data_collector.collect_data()

    except ParserException as e:
        logger.error(e)
        return 1

    except CancelledError:
        logger.info("⚠️ Программа остановлена пользователем")
        return 130

    except Exception as e:
        logger.exception(f"❌ Ошибка инициализации: {e}")
        return 1

    finally:
        logger.info("Программа завершила работу")


if __name__ == "__main__":
    asyncio.run(main())
