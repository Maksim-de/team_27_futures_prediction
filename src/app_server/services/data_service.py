from typing import Optional
from datetime import date, datetime, timedelta
from pydentic_schemas.data_schemas import PriceTableResponse


def get_id_dates(request: str):
    # Only process first entry from the request list. Update to multiprocessing later
    rqs = request[0]
    if "ticker_id" in rqs:
        id = rqs.ticker_id
    elif "query_id" in rqs:
        id = rqs.query_id
    else:
        id = ""
    date_from = rqs.date_from if rqs.date_from is not None \
        else (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    date_to = rqs.date_to if rqs.date_to is not None else datetime.now().strftime('%Y-%m-%d')
    return id, date_from, date_to


def download_prices(ticker_id: str, date_from: Optional[date], date_to: Optional[date]):
    return "Ticker prices download initiated"


def download_news(query_id: int, date_from: Optional[date], date_to: Optional[date]):
    return "News data download initiated"


def check_download_status(item_id: str):
    return "Download in progress"


def get_price_table(ticker_id: str, date_from: Optional[date], date_to: Optional[date]):
    data = [
        {"ticker_id": "BZ=F", "business_date": "2024-12-01", "open": 123, "close": 123, "high": 123, "low": 123},
        {"ticker_id": "BZ=F", "business_date": "2024-12-02", "open": 124, "close": 124, "high": 124, "low": 124}
    ]
    return PriceTableResponse(data=data)


def get_news_sentiment_table(ticker_id: str, date_from: Optional[date], date_to: Optional[date]):
    data = ""
    return PriceTableResponse(data=data)


def get_data_status():
    data = [{"item_id": "BZ-F", "min_available_date": "2024-12-01", "max_available_date": "2024-12-31"},
            {"item_id": "CL-F", "min_available_date": "2024-12-01", "max_available_date": "2024-12-31"},
            {"item_id": "NEWS_BZ-F", "min_available_date": "2024-12-01", "max_available_date": "2024-12-31"},
            {"item_id": "NEWS_CL-F", "min_available_date": "2024-12-01", "max_available_date": "2024-12-31"}
    ]
    return data


def run_price_inference():
    pass


def run_sentiment_inference():
    pass