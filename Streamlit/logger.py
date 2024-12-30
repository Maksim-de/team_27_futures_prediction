import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import date

LOGS_DIR = "logs"

def setup_logger(name):
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)

    log_file = os.path.join(LOGS_DIR, f"{name}_{date.today()}.log")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger