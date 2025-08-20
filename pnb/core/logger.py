import logging
from logging.handlers import RotatingFileHandler
import os
import coloredlogs

LOG_DIR = "logs"
LOG_FILE = "app.log"
MAX_LOG_SIZE = 1 * 1024 * 1024  # 1MB
BACKUP_COUNT = 10

os.makedirs(LOG_DIR, exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)

        # ---- Console (coloredlogs) ----
        coloredlogs.install(
            level="DEBUG",
            logger=logger,
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        )

        # ---- Rotating File Handler (with colors too) ----
        file_handler = RotatingFileHandler(
            filename=os.path.join(LOG_DIR, LOG_FILE),
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding="utf-8",
        )
        file_formatter = coloredlogs.ColoredFormatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


LOGGER = get_logger("App Logger")
