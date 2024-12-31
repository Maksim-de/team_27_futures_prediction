from fastapi import APIRouter, HTTPException, status
#ensure the PYTHONPATH includes app_server.
from pydentic_schemas.data_schemas import MessageResponseList
from pydentic_schemas.model_schemas import ModelList, PredictionRequestList, PredicitonResponse, PredictionResponseList
from pydentic_schemas.model_schemas import InferenceAttributeValueList,TrainModelResponse,TrainNewModelRequest
from services.model_service import train_ml_model, predict_price, list_models, list_inference_attributes
from services.model_service import list_inference_attribute_values, train_new_model_logic
from datetime import date
from typing import List
from logging import getLogger


router = APIRouter()
logger = getLogger("price_prediction_api")

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

    :param model_name: Model used for prediction
    :param item_id: Ticker to predict prices for
    :param start_date: start date of prediction interval
    :param end_date: end date of prediction interval
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


@router.get("/list_inference_attributes",
             response_model=List,
             status_code=status.HTTP_200_OK,
             summary="List additional attributes derived from inference")
async def list_inference_attributes_handler():
    logger.info("list_inference_attributes(+)")
    response = list_inference_attributes()
    logger.info("list_inference_attributes(-)")

    return response


@router.get("/get_inference_attribute_values",
             response_model=InferenceAttributeValueList,
             status_code=status.HTTP_200_OK,
             summary="List additional attributes derived from inference")
async def list_inference_attributes_handler(attribute_name: str, ticker_id: str, date_from: date, date_to: date):
    """
    Retrieve values of the attribute for ticker_id within specified date range

    :param attribute_name: Name of the attribute to select value for
    :param ticker_id: Ticker id
    :param date_from: Period start date
    :param date_to: Period end date
    :return:
    """
    logger.info("list_inference_attributes(+)")
    response = list_inference_attribute_values(attribute_name, ticker_id, date_from, date_to)
    logger.info("list_inference_attributes(-)")

    return response



@router.post(
    "/train_new_model",
    status_code=status.HTTP_200_OK,
    summary="Train new model using uploaded DataFrame",
    response_model=TrainModelResponse
)
async def train_new_model_handler(request: TrainNewModelRequest):
    """
    Creates new model and provides fit procedure
    :param model_name: model's name after saving
    :param shift_days: value needed to control forecasting horizon
    :param test_len: value to control  blinded period for mertics evaluetion
    :param ticker_name:  data filter for significant and ony one ticker entity
    """

    logger.info("train_new_model_handler (+)")

    # Проверка наличия загруженного DataFrame
    from api.v1.data_router import UPLOADED_DF_NEW
    if UPLOADED_DF_NEW is None:
        logger.error("No DF uploaded!")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No DataFrame uploaded yet. Call /upload_cleaned_df first."
        )

    # Фильтрация DataFrame по тикеру, если указан
    df = UPLOADED_DF_NEW
    if request.ticker_name:
        df = df.loc[df.ticker == request.ticker_name]

    try:
        result = train_new_model_logic(
            df=df,
            model_name=request.model_name,
            shift_days=request.shift_days,
            test_len=request.test_len,
            ticker_name=request.ticker_name
        )
    except Exception as e:
        logger.error(f"Error in train_new_model_handler: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

    logger.info("train_new_model_handler (-)")

    return TrainModelResponse(
        train_test_result=result["train_test_result"],
        model_stat=result["model_stat"]
    )
