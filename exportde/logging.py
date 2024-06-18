import os
import logging
import functools

__all__ = ("expo_handler", "get_logger")

LOGNAME = "ExpoLogger"


def get_logger() -> logging.Logger:
    if LOGNAME in logging.Logger.manager.loggerDict:
        return logging.getLogger(LOGNAME)
    logger = logging.getLogger(LOGNAME)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    formatter = logging.Formatter(fmt="%(asctime)s::%(levelname)s::%(message)s",
                                  datefmt="%H:%M:%S")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)

    fhandler = logging.FileHandler(filename=os.path.abspath("logs"), encoding="utf-8")
    fhandler.setLevel(logging.ERROR)
    fhandler.setFormatter(formatter)
    logger.addHandler(fhandler)
    return logger


def expo_handler(exc_type=None, msg=""):
    """Provide unified way to specify and log the exception.

    If after exception handling in a function one still occur, than it can be replaced by an exp_type
    in order to be handled by
    """
    logger = get_logger()

    def wrap(fn):
        @functools.wraps(fn)
        def _inner(*args, **kwargs):
            logger.info(f"Executing function: {fn.__name__}")
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                logger.error(exc, exc_info=True)
                if exc_type is None:
                    raise exc
                else:
                    raise exc_type(msg) from exc
        return _inner
    return wrap
