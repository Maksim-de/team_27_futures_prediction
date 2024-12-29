import os
from datetime import datetime, timedelta
import pandas as pd
import pickle
import mariadb
from db.db_config import DB_CONFIG, APP_CONFIG
from logging import getLogger
from pydentic_schemas.model_schemas import Model, ModelList, InferenceAttributeValueList, InferenceAttributeValue


logger = getLogger("price_prediction_api")


def train_ml_model(model_name: str, model_description: str, file_name: str, model_class: str, hyperparams):
    # Logic to train a new ML model
    pass


def get_data_from_db():
    logger.info("get_data_from_db(+)")
    logger.info(f"DB_CONFIG={DB_CONFIG}")

    connection = mariadb.connect(**DB_CONFIG)

    try:
        tickers = ['CL=F', 'BZ=F', 'SPY', 'QQQ']
        finbert_query = """SELECT * FROM daily_finbert_sentiment """
        feature_query = """SELECT * FROM feature_data """

        sentiment = pd.read_sql(finbert_query, connection)
        features = pd.read_sql(feature_query, connection)

        # min&max dates
        start_date = pd.to_datetime(sentiment.business_date.min())
        end_date = pd.to_datetime(sentiment.business_date.max())

        all_dates = pd.date_range(start=start_date, end=end_date)
        all_combinations = pd.MultiIndex.from_product([tickers, all_dates], names=['ticker', 'business_date']).to_frame(
            index=False)
        sentiment["business_date"] = pd.to_datetime(sentiment["business_date"])
        all_combinations = all_combinations.merge(sentiment, 'left', ['business_date', 'ticker']).merge(features,
                                                                                                        'left',
                                                                                                        [
                                                                                                            'business_date',
                                                                                                            'ticker',
                                                                                                            'asset_name'])
        all_combinations['weekday'] = pd.to_datetime(all_combinations.business_date).dt.weekday
        all_combinations['month'] = pd.to_datetime(all_combinations.business_date).dt.month
    finally:
        connection.close()

    return all_combinations


def predict_price(model_name, ticker_name, start_date, end_date):
    data = get_data_from_db()

    with open(f"models/{model_name}", "rb") as f:
        bundle = pickle.load(f)

    # распаковываем бандл
    BZ_F_model = bundle["model"]
    BZ_F_scaler = bundle["scaler"]
    BZ_F_chosen_features = bundle["chosen_features"]
    BZ_F_shifted_days = bundle["shifted_days"]

    # берем фрейм, в котором только нужный для конкретной модели тикер
    ticker_data = data.loc[data.ticker == ticker_name].ffill()

    # скейлер обучался на отобранных фичах, поэтому применяем трансформ к тоже уже отобранным
    data_for_model = BZ_F_scaler.transform(ticker_data[BZ_F_chosen_features])

    # так как модель обучалась со сдвигом, этот сдвиг надо вернуть в дату
    dates_predict = (ticker_data.business_date + timedelta(days=BZ_F_shifted_days)).tolist()
    predict = BZ_F_model.predict(data_for_model)

    result = pd.DataFrame([dates_predict, predict]).T
    result.columns = ['business_date', 'predict_value']

    return result


def list_models():
    directory = "models"
    files = os.listdir(directory)
    model_list = []
    for file in files:
        file_path = os.path.join(directory, file)
        model_name = os.path.splitext(file)[0]
        # Get file creation time
        creation_time = os.stat(file_path).st_ctime
        creation_date = datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d %H:%M:%S')
        model_row = Model(
            model_name=model_name,
            model_description=f"Pretrained model {model_name}.",
            file_name=file,
            status="Trained",
            train_date=creation_date,
            model_class="LinearRegreassion",
            hyperparams={"alpha": 0.9}
        )
        model_list.append(model_row)

    return model_list


def list_inference_attributes():
    sql = """select column_name 
                 from information_schema.columns 
                 where table_name = 'feature_data' 
                   and column_name not in ('business_date', 'created_datetime', 'ticker', 'asset_name')
                 order by column_name

    """
    connection = mariadb.connect(**DB_CONFIG)
    # Fetch the results

    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        rowset = cursor.fetchall()
        attribute_list = []

        for row in rowset:
            attribute_list.append(row[0])
    finally:
        connection.close()

    return attribute_list


def list_inference_attribute_values(attribute_name, ticker_id, date_from, date_to):
    sql = f"""select business_date, {attribute_name} 
                     from feature_data 
                     where ticker = '{ticker_id}' 
                       and business_date between '{date_from}' and '{date_to}'
                     order by business_date
        """
    connection = mariadb.connect(**DB_CONFIG)
    # Fetch the results

    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        rowset = cursor.fetchall()
        attribute_values = []

        for row in rowset:
            value_rec = InferenceAttributeValue(
                attribute_name=attribute_name,
                ticker_id=ticker_id,
                business_date=row[0],
                value=row[1]
                )
            attribute_values.append(value_rec)
    finally:
        connection.close()

    return attribute_values
