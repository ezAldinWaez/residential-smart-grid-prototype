"""RSGP decorators."""

import time

from ..utils.logger import logger


def log_excution(func: callable) -> callable:
    """Decorator to log the execution of the function.

    Args:
        func (callable): The function to log

    Returns:
        callable: The decorated function
    """
    def wrapper(*args, **kwargs):
        logger.info(
            f"Start executing {func.__name__} with args: {args} and kwargs: {kwargs}")
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(
            f"Finish executing {func.__name__} in {end_time - start_time} seconds")
        return result
    return wrapper


def log_start_end_error(start_msg: str = None, finish_msg: str = None, error_msg: str = None) -> callable:
    """Decorator generator to log when the function start and end and handle errors.

    Args:
        start_msg (str, optional): The message to log when the function start
        finish_msg (str, optional): The message to log when the function finish
        error_msg (str, optional): The message to log when the function raise an error


    Returns:
        callable: The generated decorator
    """
    def _decorator(func: callable) -> callable:
        def _wrapper(*args, **kwargs):
            sm = start_msg if start_msg else f"Start executing {func.__name__} in module {func.__module__}"
            fm = finish_msg if finish_msg else f"Finish executing {func.__name__} in module {func.__module__}"
            em = error_msg if error_msg else f"Error executing {func.__name__} in module {func.__module__}"

            logger.info(sm)
            try:
                result = func(*args, **kwargs)
                logger.info(fm)
                return result
            except Exception as e:
                logger.error(em)
                raise e
        return _wrapper
    return _decorator
