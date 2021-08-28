import logging
from typing import Optional

LOGGER: Optional[logging.Logger] = None


def init(app):
    """
    this function initialises the logging module

    Parameters
    ----------
    app : Dash
        the dash main app
    """
    global LOGGER
    LOGGER= app.logger
    [LOGGER.removeHandler(hdlr) for hdlr in LOGGER.handlers]

    _LOGGING_STDOUT_FORMAT = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s',
                                               datefmt='%H:%M:%S')
    _LOGGING_STDOUT_HANDLER = logging.StreamHandler()
    _LOGGING_STDOUT_HANDLER.setFormatter(_LOGGING_STDOUT_FORMAT)

    LOGGER.addHandler(_LOGGING_STDOUT_HANDLER)
    LOGGER.info("logging initialised")


def get_logger() -> logging.Logger:
    """
    this function return the global logger. the logging_module must be initialised before calling this function

    Returns
    -------
    logging.Logger :
        the global logger
    """
    if LOGGER:
        return LOGGER
    else:
        raise ValueError("init must be called before getting logger")
