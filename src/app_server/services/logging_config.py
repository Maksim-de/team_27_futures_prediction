import logging
from logging.handlers import TimedRotatingFileHandler
import os


def setup_logging():
    """
    Set up logger with file handler and console handler

    :return: logger
    """
    logger = logging.getLogger("price_prediction_api")
    logger.setLevel(logging.INFO)

    # Create a handler that writes log messages to a file and rotates daily
    if not os.path.exists("logs"):
        os.makedirs("logs")
    handler = TimedRotatingFileHandler(
        "logs/price_prediction_api.log", when="D", interval=1, backupCount=5
    )
    handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))

    # Add handler to the logger
    logger.addHandler(handler)

    # Add logging to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    logger.addHandler(console_handler)

    return logger

