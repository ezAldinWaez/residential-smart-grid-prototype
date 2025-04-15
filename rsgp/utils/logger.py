"""RSGP Logger."""

from pathlib import Path
import sys
from typing import Optional

import logging
import logging.handlers

from ..config import settings


def configure_logger(
    name: str = "log",
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_bytes: int = 5 * 1024 * 1024,  # 5 MB
    backup_count: int = 3
) -> logging.Logger:
    """Configure and return a logger with console and optional file handlers.

    Args:
        name: Logger name
        log_level: Minimum logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup logs to keep
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level.upper())
    logger.handlers.clear()
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.critical(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception

    return logger


logger = configure_logger(
    name="RSGP",
    log_level=settings.LOG_LEVEL,
    log_file=settings.LOG_PATH,
)
