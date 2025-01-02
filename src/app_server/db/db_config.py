import os
import json


def set_config():
    """
    Retrieve env variables and set DB and APP configs
    :return: Dict, Dict - dictionaries of config values for DB and APP
    """
    DB_CONFIG = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME')
    }
    APP_CONFIG = {
        'price_token': os.getenv('PRICE_TOKEN'),
        'news_token': os.getenv('NEWS_TOKEN')
    }
    #
    #with open('appconfig_oil.json') as f:
    #    APP_CONFIG = json.load(f)
    #    APP_CONFIG['news_token'] = news_token
    #
    return DB_CONFIG, APP_CONFIG


DB_CONFIG, APP_CONFIG = set_config()