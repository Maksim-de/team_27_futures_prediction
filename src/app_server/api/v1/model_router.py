from fastapi import APIRouter, HTTPException, status
#ensure the PYTHONPATH includes app_server.
from pydentic_schemas.data_schemas import MessageResponseList
from pydentic_schemas.model_schemas import ModelList, PredictionRequestList, PredicitonResponse, PredictionResponseList
from services.model_service import train_ml_model, predict_price, list_models
from datetime import date
from typing import List


router = APIRouter()

@router.post("/train",
             response_model=MessageResponseList,
             status_code=status.HTTP_200_OK,
             summary="Train a new ML model")
async def train_model_handler(request: ModelList):
    """
    Start model training process

    :return:
    """
    rqs = request[0]
    model_name = rqs.model_name
    model_description = rqs.model_description
    file_name = rqs.file_name
    model_class = rqs.model_class
    hyperparams = rqs.hyperparams
    result = train_ml_model(model_name, model_description, file_name, model_class, hyperparams)

    return {"message": "Model training initiated"}


@router.get("/list_models",
            response_model=ModelList,
            status_code=status.HTTP_200_OK,
            summary="List available models")
async def list_models_handler():
    """
    List available models with its statuses.
    Possible statuses: Ready, Training, Error

    :return: ModelList, see model_schemas.py
    """
    response = list_models()
    return response


@router.get("/predict_price",
             response_model=PredictionResponseList,
             status_code=status.HTTP_200_OK,
             summary="Predict price of a ticker using a model")
async def predict_price_handler(model_name: str, item_id: str, start_date: date, end_date: date):
    """
    Predict price of a ticker using a model

    :param request: PredictionRequestList, see model_schemas.py
    :return: PredictionResponseList, see model_schemas.py
    """
    #rqs = request[0]
    #model_name = rqs.model_name
    #item_id = rqs.item_id
    #start_date = rqs.start_date
    #end_date = rqs.end_date
    try:
        result_df = predict_price(model_name, item_id, start_date, end_date)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error: {e}")

    predictions: List[PredicitonResponse] = [
        PredicitonResponse(
            model_name=model_name,
            ticker_id=item_id,
            prediction_date=row["business_date"].date(),
            prediction_value=row["predict_value"],
        )
        for _, row in result_df.iterrows()
    ]

    return predictions

