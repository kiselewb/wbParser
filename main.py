import asyncio
import argparse

from asyncio import CancelledError

from loguru import logger

from core.client_api import ClientAPI
from collectors.data_collector import DataProductCollector
from collectors.id_collector import IdProductCollector
from utils.exceptions import ParserException
from utils.logger import setup_logger


async def main():
    setup_logger()

    parser = argparse.ArgumentParser(
        description="Парсер данных с WB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--mode",
        choices=["ids", "data", "full"],
        default="data",
        help="Режим работы парсера",
    )

    args = parser.parse_args()

    try:
        if args.mode == "ids":
            async with ClientAPI(True, False) as client:
                id_collector = IdProductCollector(client)
                await id_collector.collect_ids()
        else:
            async with ClientAPI(True, True) as client:
                if args.mode == "data":
                    data_collector = DataProductCollector(client)
                    await data_collector.collect_data()
                else:
                    id_collector = IdProductCollector(client)
                    await id_collector.collect_ids()
                    data_collector = DataProductCollector(client)
                    await data_collector.collect_data(is_from_file=True)

    except ParserException as e:
        logger.error(e)
        return 1

    except CancelledError:
        logger.info("⚠️ Программа остановлена пользователем")
        return 130

    except Exception as e:
        logger.exception(f"❌ Ошибка в работе программы: {e}")
        return 1

    finally:
        logger.info("Программа завершила работу")


if __name__ == "__main__":
    asyncio.run(main())
