"""RSGP logger."""

from pathlib import Path
import sys
import logging
import logging.handlers

from ..config.settings import settings


def configure_logger(name: str = "log") -> logging.Logger:
    """Configure and return a logger with console and optional file handlers.

    Args:
        * name (str): Logger name

    Returns:
        Logger: Logger object
    """
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)
    logger.handlers.clear()
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    log_path = Path(settings.LOG_PATH)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=settings.LOG_PATH,
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
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


logger = configure_logger(name="RSGP")  #: Logger: global RSGP logger instance
