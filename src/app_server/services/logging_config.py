import logging
from logging.handlers import TimedRotatingFileHandler

def setup_logging():
    logger = logging.getLogger("price_prediction_api")
    logger.setLevel(logging.INFO)

    # Create a handler that writes log messages to a file and rotates daily
    handler = TimedRotatingFileHandler(
        "logs/price_prediction_api.log", when="D", interval=1, backupCount=5
    )
    handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))

    # Add handler to the logger
    logger.addHandler(handler)

    # Optionally log to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    logger.addHandler(console_handler)

    return logger

