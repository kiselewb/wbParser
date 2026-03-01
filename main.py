import asyncio
import argparse

from asyncio import CancelledError

from loguru import logger

from core.client_api import ClientAPI
from collectors.data_collector import DataProductCollector
from collectors.id_collector import IdProductCollector
from utils.cookies_fetcher import CookiesManager
from utils.exceptions import ParserException
from utils.logger import setup_logger
from utils.report_manager import ReportManager


async def main():
    setup_logger()

    parser = argparse.ArgumentParser(
        description="Парсер данных с WB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
    Полный цикл (Сбор ID + парсинг данных по ID из файла):
    python -m main --mode full
    
    Получение ID товаров:
    python -m main --mode ids
    
    Парсинг товаров (не из файла):
    python -m main --mode data
    
    Получение Cookies:
    python -m main --mode cookies
        """,
    )

    parser.add_argument(
        "--mode",
        choices=["ids", "data", "full", "report", "cookies"],
        default="data",
        help="Режим работы парсера",
    )

    args = parser.parse_args()

    try:
        if args.mode == "ids":
            async with ClientAPI(True, False) as client:
                id_collector = IdProductCollector(client)
                await id_collector.collect_ids()
        elif args.mode in {"data", "full"}:
            async with ClientAPI(True, True) as client:
                if args.mode == "data":
                    data_collector = DataProductCollector(client)
                    await data_collector.collect_data()
                else:
                    id_collector = IdProductCollector(client)
                    await id_collector.collect_ids()
                    data_collector = DataProductCollector(client)
                    await data_collector.collect_data(is_from_file=True)
        elif args.mode == "report":
            report_manager = ReportManager("test_report")
            await report_manager.create_report()
        else:
            cookies_manager = CookiesManager()
            await cookies_manager.write_cookies()

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
