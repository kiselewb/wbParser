import sys

from loguru import logger

from config.paths import LOGS_FILE
from config.settings import logs_settings


def setup_logger(
    is_file_log: bool = logs_settings.IS_FILE_LOG,
    is_console_log: bool = logs_settings.IS_CONSOLE_LOG,
    level: str = logs_settings.LOG_LEVEL,
    rotation: str = logs_settings.LOG_ROTATION,
    compression: str = logs_settings.LOG_COMPRESSION,
):
    logger.remove()

    if is_console_log:
        logger.add(
            sys.stdout,
            level=level,
            colorize=True,
        )

    if is_file_log:
        logger.add(
            LOGS_FILE,
            level=level,
            rotation=rotation,
            compression=compression,
            enqueue=True,
        )
