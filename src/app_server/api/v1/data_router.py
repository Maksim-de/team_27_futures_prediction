from fastapi import APIRouter, HTTPException, status
#ensure the PYTHONPATH includes app_server.
from pydentic_schemas.data_schemas import TickerPriceRequestList, NewsLoadRequestList
from pydentic_schemas.data_schemas import LoadStatusRequestList, MessageResponseList, PriceTableResponse
from pydentic_schemas.data_schemas import NewsSentimentRequestList, NewsSentimentResponse, DataStatusResponseList
from services.data_service import download_prices, download_news, check_download_status, get_id_dates, get_price_table
from services.data_service import get_news_sentiment_table, get_data_status
from services.data_service import run_price_inference, run_sentiment_inference
from logging import getLogger
from datetime import date


router = APIRouter()
logger = getLogger("price_prediction_api")


@router.post("/download_prices",
            response_model=MessageResponseList,
            status_code=status.HTTP_200_OK,
            summary="Download price data for the period")
async def download_prices_handler(request: TickerPriceRequestList):
    """
    Invoke price download API for the ticker_id for requested period.
    The process connects to Yahoo Finance API and downloads ticker prices into the local database.

    :param request: TickerPriceRequestList, see data_schemas.py
    :return [{"item_id": str, "message": str}]
    """
    logger.info("Download prices endpoint (+)")

    ticker_id, date_from, date_to = get_id_dates(request)
    logger.info(f"Will download prices for {ticker_id} from {date_from} to {date_to}")

    try:
        result = download_prices(ticker_id, date_from, date_to)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error: {e}")

    response = [{"item_id": ticker_id, "message": result}]

    logger.info("Download prices endpoint (-)")
    return response


@router.post("/download_news",
            response_model=MessageResponseList,
            status_code=status.HTTP_200_OK,
            summary="Download news data for the period")
async def download_news_handler(request: NewsLoadRequestList):
    """
    Invoke news download API for the news query_id for requested period (default last 30 days).
    The process connects to Webzio API and downloads ticker prices into the local database.
    The job is submitted asynchronously, to check download status client has to call /check_download_status handler

    :param request: NewsLoadRequestList, see data_schemas.py
    :return: [{"item_id": str, "message": str}]
    """
    logger.info("Download news endpoint (+)")

    query_id, date_from, date_to = get_id_dates(request)
    try:
        result = download_news(query_id, date_from, date_to)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error: {e}")

    response = [{"item_id": query_id, "message": result}]
    logger.info("Download news endpoint (-)")

    return response


@router.get("/check_download_status",
            response_model=MessageResponseList,
            status_code=status.HTTP_200_OK,
            summary="Download news data for the period")
#async def check_download_status_handler(request: LoadStatusRequestList):
async def check_download_status_handler(item_id: str):
    """
    Check status of the last download request

    :param item_id: Id of the item to check download status for
    :return: [{"item_id": str, "message": str}]
    """

    logger.info("Check download status endpoint (+)")
    try:
        result = check_download_status(item_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error: {e}")

    response = [{"item_id": item_id, "message": result}]
    logger.info("Check download status endpoint (-)")

    return response


@router.post("/run_sentiment_inference",
            response_model=MessageResponseList,
            status_code=status.HTTP_200_OK,
            summary="Retrieve prices of a ticker for the period")
async def run_sentiment_inference_handle(request: NewsSentimentRequestList):
    """
    Run the process of calculating Finbert sentiment scores for news over specified period
    and store derived values in database

    :param request: NewsSentimentRequestList, see data_schemas.py
    :return: [{"item_id": str, "message": str}]
    """
    logger.info("Run sentiment inference endpoint (+)")

    query_id, date_from, date_to = get_id_dates(request)
    try:
        result = run_sentiment_inference(query_id, date_from, date_to)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error: {e}")

    response = [{"item_id": query_id, "message": result}]
    logger.info("Run sentiment inference endpoint (-)")

    return response


@router.post("/run_price_inference",
                 response_model=PriceTableResponse,
                 status_code=status.HTTP_200_OK,
                 summary="Retrieve prices of a ticker for the period")
async def run_price_inference_handler(request: TickerPriceRequestList):
    """
    Run technical analysis for ticker prices over specified period and store derived values in database

    :param request: TickerPriceRequestList, see data_schemas.py
    :return: [{"item_id": str, "message": str}]
    """
    logger.info("Run price inference endpoint (+)")

    ticker_id, date_from, date_to = get_id_dates(request)
    try:
        result = run_price_inference(ticker_id, date_from, date_to)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error: {e}")

    response = [{"item_id": ticker_id, "message": result}]
    logger.info("Run sentiment inference endpoint (-)")

    return response


@router.get("/get_price_table",
            response_model=PriceTableResponse,
            status_code=status.HTTP_200_OK,
            summary="Retrieve prices of a ticker for the period")
async def get_price_table_handler(ticker_id: str, date_from: date, date_to: date):
    """
    Retrieve prices for the ticker_id over the specified period. This is useful for displaying price charts in UI

    :param request: TickerPriceRequestList, see data_schemas.py
    :return: PriceTableResponse, see data_schemas.py
    """
    logger.info("Get Price Table endpoint (+)")

    #ticker_id, date_from, date_to = get_id_dates(request)
    try:
        result = get_price_table(ticker_id, date_from, date_to)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error: {e}")
    logger.info("Get Price Table endpoint (-)")

    return result


@router.get("/get_news_sentiment",
            response_model=NewsSentimentResponse,
            status_code=status.HTTP_200_OK,
            summary="Retrieve finbert sentiments for the period")
async def get_news_sentiment(ticker_id: str, date_from: date, date_to: date):
    """
    Retrieve finbert sentiment data for the news related to the ticker over specified period (default last 30 days)
    Sentiment is calculated over different dimensions and lags. Check daily_finbert_sentiment table in the Database
    :param request: NewsSentimentRequestList, see data_schemas.py
    :return: a table in format of NewsSentimentResponse, see data_schemas.py
    """
    logger.info("Get News Sentiment endpoint (+)")

    #ticker_id, date_from, date_to = get_id_dates(request)
    try:
        result = get_news_sentiment_table(ticker_id, date_from, date_to)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error: {e}")
    logger.info("Get News Sentiment endpoint (-)")

    return result


@router.get("/get_data_status",
            response_model=DataStatusResponseList,
            status_code=status.HTTP_200_OK,
            summary="Retrieve average news sentiment for the period")
async def get_data_status_handler():
    """
    Return data intervals for which ticker and news data is available in the DB.
    :return: a list in format DataStatusResponse, see data_schemas.py
    """
    logger.info("Get data Status endpoint (+)")

    result = get_data_status()

    logger.info("Get data Status endpoint (-)")
    return result


@router.post("/cleanup", summary="Clean up data")
async def cleanup_data_handler():
    """
    For now just a placeholder
    :return: {"message": str}
    """
    return {"message": "Data cleanup completed"}
