from typing import Optional
from datetime import date, datetime, timedelta
from pydentic_schemas.data_schemas import PriceTableResponse, NewsSentimentResponseRow, NewsSentimentResponse
from logging import getLogger


logger = getLogger("price_prediction_api")


def get_id_dates(request: str):
    # Only process first entry from the request list. Update to multiprocessing later
    logger.info("get_id_dates (+)")

    rqs = request[0]
    logger.info(f"get_id_dates type={type(request)}; request: {rqs}")

    try:
        id = rqs.ticker_id
    except Exception as e:
        try:
            id = rqs.query_id
        except Exception as e:
            id = ""
    date_from = rqs.date_from if rqs.date_from is not None \
        else (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    date_to = rqs.date_to if rqs.date_to is not None else datetime.now().strftime('%Y-%m-%d')

    logger.info("get_id_dates (-)")

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
    example_row = NewsSentimentResponseRow(
        ticker_id="BZ=F",
        business_date=date(2024, 1, 1),
        sentiment="Positive",
        avg_finbert_sentiment=0.75,
        sentiment_std=0.12,
        weighted_avg_finbert_sentiment=0.80,
        avg_finbert_sentiment_lag1=0.70,
        weighted_avg_finbert_sentiment_lag1=0.78,
        avg_finbert_sentiment_diff1=0.05,
        weighted_avg_finbert_sentiment_diff1=0.02,
        avg_finbert_sentiment_lag2=None,
        weighted_avg_finbert_sentiment_lag2=None,
        avg_finbert_sentiment_diff2=None,
        weighted_avg_finbert_sentiment_diff2=None,
        avg_finbert_sentiment_lag3=None,
        weighted_avg_finbert_sentiment_lag3=None,
        avg_finbert_sentiment_diff3=None,
        weighted_avg_finbert_sentiment_diff3=None,
        avg_finbert_sentiment_lag7=None,
        weighted_avg_finbert_sentiment_lag7=None,
        avg_finbert_sentiment_diff7=None,
        weighted_avg_finbert_sentiment_diff7=None,
        finbert_sentiment_acceleration=None,
        weighted_finbert_sentiment_acceleration=None,
        avg_finbert_sentiment_ma_7=0.72,
        weighted_avg_finbert_sentiment_ma_7=0.76,
        avg_finbert_sentiment_ma_15=0.70,
        weighted_avg_finbert_sentiment_ma_15=0.74,
        avg_finbert_sentiment_ma_30=0.68,
        weighted_avg_finbert_sentiment_ma_30=0.70,
        price_change=1.5,
        avg_finbert_sentiment_ma_30_shifted_45=None,
        weighted_avg_finbert_sentiment_ma_30_shifted_45=None,
    )

    return NewsSentimentResponse(data=[example_row])


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