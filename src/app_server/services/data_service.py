from typing import Optional
from datetime import date, datetime, timedelta
from pydentic_schemas.data_schemas import PriceTableResponse, NewsSentimentResponseRow, NewsSentimentResponse
from pydentic_schemas.data_schemas import DataStatusResponse, PriceTableRow
from logging import getLogger
from db.db_config import DB_CONFIG
import mariadb

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
    sql = f"""SELECT *
                   FROM market_data
                   where ticker = '{ticker_id}'
                     and business_date between '{date_from}' and '{date_to}'        
                       ORDER BY business_date"""
    connection = mariadb.connect(**DB_CONFIG)
    # Fetch the results

    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        rowset = cursor.fetchall()
        data_list = []

        for row in rowset:
            data_row = PriceTableRow(
                open=row[0],
                high=row[1],
                low=row[2],
                close=row[3],
                adj_close=row[4],
                volume=row[5],
                ticker=row[6],
                asset_name=row[7],
                business_date=row[8],
                created_datetime=row[9]
            )
            data_list.append(data_row)
    finally:
        connection.close()

    return PriceTableResponse(data=data_list)


def get_news_sentiment_table(ticker_id: str, date_from: Optional[date], date_to: Optional[date]):

    sql = f"""SELECT *
               FROM daily_finbert_sentiment
               where ticker = '{ticker_id}'
                 and business_date between '{date_from}' and '{date_to}'        
                   ORDER BY business_date"""
    connection = mariadb.connect(**DB_CONFIG)
    # Fetch the results

    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        rowset = cursor.fetchall()
        data_list = []

        for row in rowset:
            data_row = NewsSentimentResponseRow(
                ticker=row[0],
                asset_name=row[1],
                business_date=row[2],
                close=row[3],
                avg_finbert_sentiment=row[4],
                sentiment_std=row[5],
                weighted_avg_finbert_sentiment=row[6],
                avg_finbert_sentiment_lag1=row[7],
                weighted_avg_finbert_sentiment_lag1=row[8],
                avg_finbert_sentiment_diff1=row[9],
                weighted_avg_finbert_sentiment_diff1=row[10],
                avg_finbert_sentiment_lag2=row[11],
                weighted_avg_finbert_sentiment_lag2=row[12],
                avg_finbert_sentiment_diff2=row[13],
                weighted_avg_finbert_sentiment_diff2=row[14],
                avg_finbert_sentiment_lag3=row[15],
                weighted_avg_finbert_sentiment_lag3=row[16],
                avg_finbert_sentiment_diff3=row[17],
                weighted_avg_finbert_sentiment_diff3=row[18],
                avg_finbert_sentiment_lag7=row[19],
                weighted_avg_finbert_sentiment_lag7=row[20],
                avg_finbert_sentiment_diff7=row[21],
                weighted_avg_finbert_sentiment_diff7=row[22],
                finbert_sentiment_acceleration=row[23],
                weighted_finbert_sentiment_acceleration=row[24],
                avg_finbert_sentiment_ma_7=row[25],
                weighted_avg_finbert_sentiment_ma_7=row[26],
                avg_finbert_sentiment_ma_15=row[27],
                weighted_avg_finbert_sentiment_ma_15=row[28],
                avg_finbert_sentiment_ma_30=row[29],
                weighted_avg_finbert_sentiment_ma_30=row[30],
                price_change=row[31],
                avg_finbert_sentiment_ma_30_shifted_45=row[32],
                weighted_avg_finbert_sentiment_ma_30_shifted_45=row[33]
            )
            data_list.append(data_row)
    finally:
        connection.close()

    return NewsSentimentResponse(data=data_list)


def get_data_status():
    """data = [{"item_id": "BZ-F", "min_available_date": "2024-12-01", "max_available_date": "2024-12-31"},
            {"item_id": "CL-F", "min_available_date": "2024-12-01", "max_available_date": "2024-12-31"},
            {"item_id": "NEWS_BZ-F", "min_available_date": "2024-12-01", "max_available_date": "2024-12-31"},
            {"item_id": "NEWS_CL-F", "min_available_date": "2024-12-01", "max_available_date": "2024-12-31"}
            ]"""
    sql = """SELECT ticker, 
                    cast(min(business_date) as date) AS min_available_date, 
                    cast(max(business_date) as date) AS max_available_date
               FROM market_data  
               GROUP BY ticker
             UNION ALL
             SELECT "NEWS_DATA" AS ticker,
                    cast(min(published_timestamp) as date) AS min_available_date, 
                    cast(max(published_timestamp) as date) AS max_available_date
               FROM news_data       
               ORDER BY ticker"""
    connection = mariadb.connect(**DB_CONFIG)
    # Fetch the results

    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        rowset = cursor.fetchall()
        data_list = []

        for row in rowset:
            data_row = DataStatusResponse(
                item_id=row[0],
                min_available_date=row[1],
                max_available_date=row[2]
            )
            data_list.append(data_row)
    finally:
        connection.close()

    return data_list


def run_price_inference():
    pass


def run_sentiment_inference():
    pass
