"""RSGP logger."""

from pathlib import Path
from typing import Optional
import sys
import logging
import logging.handlers

from ..config.settings import settings


def configure_logger(
    name: str = "log",
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_bytes: int = 5 * 1024 * 1024,  # 5 MB
    backup_count: int = 3
) -> logging.Logger:
    """Configure and return a logger with console and optional file handlers.

    Args:
        name (str): Logger name.
        log_level (str): Minimum logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file (str, optional): Path to log file.
        max_bytes (int, optional): Maximum log file size before rotation, default is 5 MB.
        backup_count (int, optional): Number of backup logs to keep, default is 3.

    Returns:
        Logger: Logger object.
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
        logger.critical("Uncaught exception", exc_info=(
            exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception

    return logger


logger = configure_logger(
    name="RSGP",
    log_level=settings.LOG_LEVEL,
    log_file=settings.LOG_PATH,
    max_bytes=settings.LOG_MAX_BYTES,
    backup_count=settings.LOG_BACKUP_COUNT,
)
