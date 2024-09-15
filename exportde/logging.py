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
    stream_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)

    logdir = os.path.expanduser("~/.exportde")
    if not os.path.exists(logdir):
        os.mkdir(logdir)
    filename = os.path.join(logdir, "logs")
    fhandler = logging.FileHandler(filename=filename, encoding="utf-8")
    fhandler.setLevel(logging.ERROR)
    fhandler.setFormatter(formatter)
    logger.addHandler(fhandler)
    return logger


def expo_handler(fn):
    """Provide unified way to log execution."""
    logger = get_logger()

    @functools.wraps(fn)
    def wrap(*args, **kwargs):
        logger.info(f"Executing function: {fn.__name__}")
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            logger.error(exc, exc_info=True)
            raise exc
    return wrap
