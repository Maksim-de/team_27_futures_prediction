import os
from datetime import datetime, timedelta
import pandas as pd
import pickle
import mariadb
from db.db_config import DB_CONFIG, APP_CONFIG
from logging import getLogger
from pydentic_schemas.model_schemas import Model, ModelList, InferenceAttributeValueList, InferenceAttributeValue
import ntpath
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error

logger = getLogger("price_prediction_api")


def train_ml_model(model_name: str, model_description: str, file_name: str, model_class: str, hyperparams):
    # Logic to train a new ML model
    pass


def get_data_from_db():
    """
    Retrieve data from DB to use in predict_price
    :return: pandas dataframe
    """
    logger.info("get_data_from_db(+)")
    logger.info(f"DB_HOST={DB_CONFIG['host']}")

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
        all_combinations = (all_combinations.
                merge(sentiment, 'left', ['business_date', 'ticker']).
                merge(features, 'left',['business_date','ticker','asset_name'])
        )
        all_combinations['weekday'] = pd.to_datetime(all_combinations.business_date).dt.weekday
        all_combinations['month'] = pd.to_datetime(all_combinations.business_date).dt.month
    finally:
        connection.close()

    return all_combinations


def predict_price(model_name, ticker_name, start_date, end_date, data_source="db"):
    """
    Predict price of the financial instrument

    :param model_name: model name to be used for prediction
    :param ticker_name: ticker
    :param start_date: start date of prediction period
    :param end_date: end date of prediction period
    :return: ['business_date', 'predict_value']
    """
    logger.info(f"predict_price(+)")
    models_dir = find_model_folder(".")
    file_path = f"{models_dir}/{model_name}.pkl"
    logger.info(f"Found model file: {file_path}")

    with open(file_path, "rb") as f:
        bundle = pickle.load(f)

    BZ_F_model = bundle["model"]
    BZ_F_scaler = bundle["scaler"]
    BZ_F_shifted_days = bundle["shifted_days"]
    BZ_F_chosen_features = bundle.get("chosen_features", [])

    if data_source == "db":
        data = get_data_from_db()
        ticker_data = data.loc[data.ticker == ticker_name].ffill()

    elif data_source == "uploaded_file":
        from api.v1.data_router import UPLOADED_DF_NEW
        if UPLOADED_DF_NEW is None:
            raise ValueError(
                "UPLOADED_DF_NEW is None. Нажмите 'Загрузить очищенный DataFrame' на page2, прежде чем делать предикт из памяти.")
        data = UPLOADED_DF_NEW
        ticker_data = data.loc[data.ticker == ticker_name].ffill()
    else:
        raise ValueError(f"Неизвестный data_source: {data_source}")

    # Дальше логика предикта

    data_for_model = BZ_F_scaler.transform(ticker_data[BZ_F_chosen_features])
    dates_predict = (ticker_data.business_date + timedelta(days=BZ_F_shifted_days)).tolist()
    predict_values = BZ_F_model.predict(data_for_model)

    result = pd.DataFrame({"business_date": dates_predict, "predict_value": predict_values})
    result = (result.loc[result.business_date.astype(str)>=str(start_date)]
                    .loc[result.business_date.astype(str)<=str(end_date)])

    logger.info(f"predict_price(-)")
    return result


def find_model_folder(root_folder):
    """
    Inside docker image relative location of the model folder will be different from the local setup.
    This function traverses through the nested directories from the root and returns location of "models" directory.
    :param root_folder: str
    :return: str
    """
    for dirpath, dirnames, filenames in os.walk(root_folder):
        if "models" in dirpath and "venv" not in dirpath:
            return dirpath
    return []

def find_and_list_model_files(root_folder):
    """
    List model files in "models" directory
    :param root_folder: str
    :return: str
    """
    models_dir = find_model_folder(root_folder)
    return [os.path.join(models_dir, file) for file in os.listdir(models_dir)]



def list_models():
    """
    List trained models
    :return: List(Model)
    """
    logger.info(f"list_models(+)")

    files = find_and_list_model_files(".")
    model_list = []
    for file in files:
        file_name = ntpath.basename(file)
        model_name = file_name.split('.')[0]
        # Get file creation time
        creation_time = os.stat(file).st_ctime
        creation_date = datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d %H:%M:%S')
        model_row = Model(
            model_name=model_name,
            model_description=f"Pretrained model {model_name}.",
            file_name=file_name,
            status="Trained",
            train_date=creation_date,
            model_class="LinearRegreassion",
            hyperparams={"alpha": 0.9}
        )
        model_list.append(model_row)

    logger.info(f"list_models(-)")
    return model_list


def list_inference_attributes():
    """
    Return a list of inference attribute names available in the database
    :return:
    """
    logger.info(f"list_inference_attributes(+)")

    sql = """select column_name 
                 from information_schema.columns 
                 where table_name = 'feature_data' 
                   and column_name not in ('business_date', 'created_datetime', 'ticker', 'asset_name')
                 order by column_name

    """
    logger.info(f"DB_CONFIG={DB_CONFIG}")
    connection = mariadb.connect(**DB_CONFIG)
    logger.info(f"Connected to DB")
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

    logger.info(f"list_inference_attributes(-)")
    return attribute_list


def list_inference_attribute_values(attribute_name, ticker_id, date_from, date_to):
    """
    Return a list of values of the attribute for the ticker within specified period
    :param attribute_name:
    :param ticker_id:
    :param date_from:
    :param date_to:
    :return:
    """
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


def train_new_model_logic(df, model_name, shift_days, test_len, ticker_name=None):
    """
    Train a new model usiung uploaded dataset

    :param df: uploaded frame
    :param model_name: name after saving
    :param shift_days: value needed to control forecasting horizon
    :param test_len: value to control  blinded period for mertics evaluetion
    :param ticker_name: data filter for significant and ony one ticker entity
    """
    logger.info("train_new_model_logic (+)")

    # заполняем пропуски если они все-таки просочились
    if ticker_name is not None:
        df = df.loc[df.ticker==ticker_name].sort_values('business_date').ffill()
    else:
        df = df.sort_values('business_date').ffill()

    # делаем смещение и удаляем целевую переменную
    # close тоже удаляем, чтобы не было привязки к последнему известному значению

    df['next_day_close'] = df['close'].shift(-shift_days).ffill()
    df = df.iloc[:-shift_days]
    y = df['next_day_close']

    # удаляем явное обозначение цены чтобы не было застревания на этих признаках
    df.drop(['close','next_day_close','open', 'high', 'low', 'adj_close'],axis=1, inplace=True)

    logger.debug(f"Result frame columns: {df.columns}")

    # проверим что данных достаточно
    X = df.select_dtypes(include=[np.number]).copy()
    if len(X) <= test_len:
        raise Exception("Not enough data for the given test_len")

    # сначала обучим на трейне, замерим метрики и обучим на полном датасете
    dates_train = df.iloc[:-(test_len)].business_date
    dates_test = df.iloc[-test_len:].business_date
    X_train = X.iloc[:-test_len]
    y_train = y.iloc[:-test_len]
    X_test = X.iloc[-test_len:]
    y_test = y.iloc[-test_len:]

    logger.info("scaler apply")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)


    model = Ridge()
    model.fit(X_train_scaled, y_train)

    y_train_pred = model.predict(X_train_scaled)
    y_test_pred = model.predict(X_test_scaled)

    train_mse = mean_squared_error(y_train, y_train_pred)
    test_mse = mean_squared_error(y_test, y_test_pred)
    train_mape = mean_absolute_percentage_error(y_train, y_train_pred)
    test_mape = mean_absolute_percentage_error(y_test, y_test_pred)


    # теперь на полном датасете
    X_train_scaled = scaler.fit_transform(X)
    model = Ridge()
    model.fit(X_train_scaled, y)

    # Сохраняем модель в словарь
    bundle = {
        "model": model,
        "scaler": scaler,
        "shifted_days": shift_days,
        # Если в predict_price вы ожидаете "chosen_features",
        # можно добавить:
        "chosen_features": list(X_train.columns)
    }

    # Сохраняем в models/{model_name}.pkl через pickle
    models_dir = find_model_folder(".")
    if not os.path.exists(models_dir):
        models_dir = "models"
        os.makedirs(models_dir)
    file_name = f"{model_name}.pkl"
    file_path = os.path.join(models_dir, file_name)

    with open(file_path, "wb") as f:
        pickle.dump(bundle, f)

    logger.info(f"Model {model_name} saved to {file_path}")

    train_test_result = {
        "dates_train": dates_train.tolist(),
        "y_train": y_train.tolist(),
        "y_train_pred": y_train_pred.tolist(),
        "dates_test": dates_test.tolist(),
        "y_test": y_test.tolist(),
        "y_test_pred": y_test_pred.tolist(),
        "ticker_name": ticker_name,
    }

    model_stat = {
        "model_name": model_name,
        "shift_days": shift_days,
        "test_len": test_len,
        "train_mse": train_mse,
        "test_mse": test_mse,
        "train_mape": train_mape,
        "test_mape": test_mape,
    }

    result = {"train_test_result":train_test_result,"model_stat":model_stat}
    logger.info("train_new_model_logic (-)")
    return result
