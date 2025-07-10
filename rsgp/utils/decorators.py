"""RSGP decorators."""

import time

from ..utils.logger import logger


def log(func: callable) -> callable:
    """Decorator to log the execution of the function.

    Args:
        func (callable): The function to log.

    Returns:
        callable: The decorated function.
    """
    def wrapper(*args, **kwargs):
        logger.info(
            f"Executing {func.__name__} with args: {args} and kwargs: {kwargs}")
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(
            f"Finished executing {func.__name__} in {end_time - start_time} seconds")
        return result
    return wrapper
