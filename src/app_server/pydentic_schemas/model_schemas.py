from pydantic import BaseModel, Field, ConfigDict
from typing import Union, Dict, List
from datetime import date, datetime


class Model(BaseModel):
    #model_config = ConfigDict(protected_namespaces=())
    model_name: str = Field(..., title="Unique name of the model")
    model_description: str = Field(..., title="Model description")
    file_name: str = Field(..., title="Model file name")
    status: str = Field(..., title="Model status: ready, training, error")
    train_date: datetime = Field(..., description="Model training date")
    model_class: str = Field(..., title="Model class")
    hyperparams: Dict[str, Union[str, int, float, bool, List[Union[str, int, float, bool]]]] = Field(
        ..., title="Hyperparameters of the model")

    class Config:
        schema_extra = {
            "example": {
                "model_name": "Model_123",
                "model_description": "My sample model",
                "file_name": "model_123.pkl",
                "status": "Ready",
                "train_date": "2024-01-01 14:00:59",
                "model_class": "LinearRegression",
                "hyperparams": {
                    "learning_rate": 0.001,
                    "batch_size": 32,
                    "optimizer": "adam",
                    "dropout_rate": 0.5,
                    "layers": [64, 128, 256],
                    "use_batch_norm": True
                }
            }
        }


class PredicitonRequest(BaseModel):
    model_name: str = Field(..., title="Model for Prediction")
    ticker_id: str = Field(..., title="Ticker id for prediction")
    start_date: date = Field(..., Title="Start date for price prediction")
    end_date: date = Field(..., Title="End date for price prediction")

    class Config:
        schema_extra = {
            "example": {
                "model_name": "Model_123",
                "ticker_id": "CL=F",
                "start_date": "2024-12-01",
                "end_Date": "2024-12-01"
            }
        }


class PredicitonResponse(BaseModel):
    model_name: str = Field(..., title="Model for Prediction")
    ticker_id: str = Field(..., title="Ticker id for prediction")
    prediction_date: date = Field(..., Title="Start date for price prediction")
    prediction_value: float = Field(..., Title="Prediction value of the ticker for given prediction date")

    class Config:
        schema_extra = {
            "example": {
                "model_name": "Model_123",
                "ticker_id": "CL=F",
                "prediction_date": "2024-12-01",
                "prediction_value": 1234.56
            }
        }

class InferenceAttributeValue(BaseModel):
    attribute_name: str = Field(..., title="Attribute name")
    ticker_id: str = Field(..., title="Ticker id")
    business_date: date = Field(..., Title="Start date for price prediction")
    value: float = Field(..., Title="Attribute value for business date")

    class Config:
        schema_extra = {
            "example": {
                "attribute_name": "rsi",
                "ticker_id": "CL=F",
                "business_date": "2024-12-01",
                "value": 62.729
            }
        }

class TrainNewModelRequest(BaseModel):
    model_name: str = Field(..., title="Название модели для сохранения")
    shift_days: int = Field(20, title="Сдвиг дней для прогнозирования")
    test_len: int = Field(50, title="Длина тестового набора")
    ticker_name: str = Field(None, title="Название тикера для фильтрации данных")

    class Config:
        schema_extra = {
            "example": {
                "model_name": "ridge_model_2024",
                "shift_days": 20,
                "test_len": 50,
                "ticker_name": "CL=F"
            }
        }

class TrainModelResponse(BaseModel):
    train_test_result: dict = Field(..., title="Результаты тренировки и тестирования")
    model_stat: dict = Field(..., title="Статистика модели")
    class Config:
        schema_extra = {
            "example": {
                "train_test_result": {
                    "dates_train": ["2024-01-01", "2024-01-02", ...],
                    "y_train": [100.0, 101.5, ...],
                    "y_train_pred": [99.8, 101.3, ...],
                    "dates_test": ["2024-02-01", "2024-02-02", ...],
                    "y_test": [102.0, 103.5, ...],
                    "y_test_pred": [101.7, 103.4, ...],
                    "ticker_name": "CL=F"
                },
                "model_stat": {
                    "model_name": "ridge_model_2024",
                    "shift_days": 5,
                    "test_len": 30,
                    "train_mse": 0.25,
                    "test_mse": 0.30,
                    "train_mape": 2.5,
                    "test_mape": 3.0
                }
            }
        }

ModelList = List[Model]
PredictionRequestList = List[PredicitonRequest]
PredictionResponseList = List[PredicitonResponse]
InferenceAttributeValueList = List[InferenceAttributeValue]
TrainModelResponseList = List[TrainModelResponse]
TrainNewModelRequestList = List[TrainNewModelRequest]