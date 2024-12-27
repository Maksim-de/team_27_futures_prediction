from pydantic import BaseModel, Field, ConfigDict
from typing import Union, Dict, List
from datetime import date


class Model(BaseModel):
    #model_config = ConfigDict(protected_namespaces=())
    model_name: str = Field(..., title="Unique name of the model")
    model_description: str = Field(..., title="Model description")
    file_name: str = Field(..., title="Model file name")
    status: str = Field(..., title="Model status: ready, training, error")
    train_date: date = Field(..., description="Model training date")
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
                "train_date": "2024-01-01",
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


ModelList = List[Model]
PredictionRequestList = List[PredicitonRequest]
PredictionResponseList = List[PredicitonResponse]