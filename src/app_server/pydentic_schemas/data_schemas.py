from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import date, datetime


class NewsLoadRequest(BaseModel):
    query_id: str = Field(..., title="News Query Id")
    date_from: Optional[date] = Field(None, description="Start date for the news data period, default: 30 days ago")
    date_to: Optional[date] = Field(None, description="End date for the news data period, default: yesterday")
    api_type: Literal["filterWebContent", "filterArchiveNews"] = Field(
        default="filterWebContent",
        description='Type of API to use, either "filterWebContent" or "filterArchiveNews"'
    )

    class Config:
        schema_extra = {
            "example": {
                "query_id": 123,
                "date_from": "2024-01-01",
                "date_to": "2024-01-31",
                "api_type": "filterWebContent"
            }
        }

class TickerPriceRequest(BaseModel):
    ticker_id: str = Field(..., title="Ticker Id")
    date_from: Optional[date] = Field(None, description="Start date of the period, default: 30 days ago")
    date_to: Optional[date] = Field(None, description="End date of the period, default: yesterday")

    class Config:
        schema_extra = {
            "example": {
                "ticker_id": "CL=F",
                "date_from": "2024-01-01",
                "date_to": "2024-01-31"
            }
        }


class LoadStatusRequest(BaseModel):
    item_id: str = Field(..., title="Ticker Id or 'NEWS'")

    class Config:
        schema_extra = {
            "example_1": {
                "item_id": "CL=F",
                "message": "Download initiated"
            },
            "example_2": {
                "item_id": "CL=F",
                "message": "Download in progress, 500 records loaded so far."
            }
        }

class MessageResponse(BaseModel):
    item_id: str = Field(..., title="Item id")
    message: str = Field(..., title="Message")

    class Config:
        schema_extra = {
            "example": {
                "item_id": "CL=F",
            }
        }


class PriceTableRow(BaseModel):
    open: Optional[float] = Field(...)
    high: Optional[float] = Field(...)
    low: Optional[float] = Field(...)
    close: Optional[float] = Field(...)
    adj_close: Optional[float] = Field(...)
    volume: Optional[float] = Field(...)
    ticker: str = Field(...)
    asset_name: str = Field(...)
    business_date: date = Field(...)
    created_datetime: Optional[datetime] = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "business_date": "2024-12-05",
                "ticker": "CL=F",
                "open": 76.69,
                "close": 76.08,
                "high": 76.45,
                "low": 74.26
            }
        }

class PriceTableResponse(BaseModel):
    data: List[PriceTableRow]


class NewsSentimentRequest(BaseModel):
    ticker_id: str = Field(..., title="Ticker Id")
    date_from: Optional[date] = Field(None, description="Start date for the news data period, default: 30 days ago")
    date_to: Optional[date] = Field(None, description="End date for the news data period, default: yesterday")

    class Config:
        schema_extra = {
            "example": {
                "ticker_id": "CL=F",
                "date_from": "2024-01-01",
                "date_to": "2024-01-31"
            }
        }


class NewsSentimentResponseRow(BaseModel):
    ticker: str = Field(..., title="Item id")
    asset_name: str = Field(..., title="Asset Name")
    business_date: date = Field(..., Title="Business Date")
    close: Optional[float] = Field(...)
    avg_finbert_sentiment: Optional[float] = Field(...)
    sentiment_std: Optional[float] = Field(...)
    weighted_avg_finbert_sentiment: Optional[float] = Field(...)
    avg_finbert_sentiment_lag1: Optional[float] = Field(...)
    weighted_avg_finbert_sentiment_lag1: Optional[float] = Field(...)
    avg_finbert_sentiment_diff1: Optional[float] = Field(...)
    weighted_avg_finbert_sentiment_diff1: Optional[float] = Field(...)
    avg_finbert_sentiment_lag2: Optional[float] = Field(...)
    weighted_avg_finbert_sentiment_lag2: Optional[float] = Field(...)
    avg_finbert_sentiment_diff2: Optional[float] = Field(...)
    weighted_avg_finbert_sentiment_diff2: Optional[float] = Field(...)
    avg_finbert_sentiment_lag3: Optional[float] = Field(...)
    weighted_avg_finbert_sentiment_lag3: Optional[float] = Field(...)
    avg_finbert_sentiment_diff3: Optional[float] = Field(...)
    weighted_avg_finbert_sentiment_diff3: Optional[float] = Field(...)
    avg_finbert_sentiment_lag7: Optional[float] = Field(...)
    weighted_avg_finbert_sentiment_lag7: Optional[float] = Field(...)
    avg_finbert_sentiment_diff7: Optional[float] = Field(...)
    weighted_avg_finbert_sentiment_diff7: Optional[float] = Field(...)
    finbert_sentiment_acceleration: Optional[float] = Field(...)
    weighted_finbert_sentiment_acceleration: Optional[float] = Field(...)
    avg_finbert_sentiment_ma_7: Optional[float] = Field(...)
    weighted_avg_finbert_sentiment_ma_7: Optional[float] = Field(...)
    avg_finbert_sentiment_ma_15: Optional[float] = Field(...)
    weighted_avg_finbert_sentiment_ma_15: Optional[float] = Field(...)
    avg_finbert_sentiment_ma_30: Optional[float] = Field(...)
    weighted_avg_finbert_sentiment_ma_30: Optional[float] = Field(...)
    price_change: Optional[float] = Field(...)
    avg_finbert_sentiment_ma_30_shifted_45: Optional[float] = Field(...)
    weighted_avg_finbert_sentiment_ma_30_shifted_45: Optional[float] = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "ticker": "BZ=F",
                "asset_name": "BRENT",
                "business_date": "2024-01-01",
                "avg_finbert_sentiment": 0.188406,
                "sentiment_std": 0.52698
            }
        }

class NewsSentimentResponse(BaseModel):
    data: List[NewsSentimentResponseRow]


class DataStatusResponse(BaseModel):
    item_id: str = Field(..., title="Item id")
    min_available_date: date = Field(..., Title="Min available Date")
    max_available_date: date = Field(..., Title="Max available Date")
    class Config:
        schema_extra = {
            "example": {
                "item_id": "CL=F",
                "min_available_date": "2021-09-01",
                "max_available_date": "2024-11-30"
            }
        }


NewsLoadRequestList = List[NewsLoadRequest]
NewsSentimentRequestList = List[NewsSentimentRequest]
TickerPriceRequestList = List[TickerPriceRequest]
LoadStatusRequestList = List[LoadStatusRequest]
MessageResponseList = List[MessageResponse]
DataStatusResponseList = List[DataStatusResponse]
NewsSentimentResponseList = List[NewsSentimentResponseRow]

# create simple str for transformation before data uploading
# it's okay, we don't have to large datasets because of aggregation data nature
class DataBase64(BaseModel):
    data_base64: str