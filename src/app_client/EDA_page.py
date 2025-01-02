import pandas as pd
import numpy as np
import streamlit as st
import handler
import aiohttp
import asyncio
from handler import *
from urllib.parse import urlencode
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import plotly.express as px
from logger import setup_logger
from main import *
import base64

logger = setup_logger("EDA")


def run(flag):
    logger.debug("Starting application")
    st.header('Анализ данных и прогнозирование')
    tickers = ['BZ=F','CL=F', 'SPY', 'QQQ']
    option = st.sidebar.selectbox('Выберите тикер', tickers)
    today = datetime.datetime.now()
    last_year = today.year - 1
    last_date = datetime.date(last_year, 1, 1)
    period_end = today + datetime.timedelta(days=7)
    period_start = today - datetime.timedelta(days=60)

    d = st.sidebar.date_input(
        "Выберите период",
        (last_date, today),
        max_value=today,
        format="MM.DD.YYYY",
    )
    if d:
        start_date, end_date = d
        logger.info(f"Selected date range: {start_date} - {end_date}")


    if option:
        params = {"ticker_id": option, "date_from": start_date, "date_to": end_date}


    async def zap(flag):
        logger.debug(f"Starting data fetching for ticker: {option}")
        if flag == 1: # БД
            results = await asyncio.gather(
                get_data(url_download_prices, params),
                get_data(url_list_atributes, params=''),
                get_data(url_get_list_model, params='')
            )
            result_fit, option_indicators, option_model = results
            df = json_to_dataframe(result_fit)
        elif flag == 2: # csv
            df_csv = st.session_state.data
            results = await asyncio.gather(
                get_data(url_list_atributes, params=''),
                get_data(url_get_list_model, params='')
            )
            option_indicators, option_model = results
            df_csv['business_date'] = pd.to_datetime(df_csv['business_date'])
            df = df_csv[(df_csv['ticker'] == option) & (df_csv['business_date'].dt.date > start_date) & (
                    df_csv['business_date'].dt.date < end_date)]
            st.subheader('Данные из загруженного файла')
            st.dataframe(df_csv.head(5))
        logger.debug(f"End json_to_dataframe download price: {option}")
        logger.debug(f"Options indicatyors: {option_indicators}")
        atr = st.sidebar.multiselect('Доступные показатели', option_indicators, default='sma')
        all_indicator_dfs = pd.DataFrame()
        df_model = json_to_dataframe(option_model).dropna(subset=['model_name'])
        logger.debug(f"End json_to_dataframe option model: {option}")
        st.sidebar.write('Выбор модели для предсказания')
        st.session_state['available_models'] = [x for x in df_model['model_name'] if x is not None and x !='']
        model_name = st.sidebar.selectbox('Доступные модели', st.session_state['available_models'], key='updated_model_selectbox')
        k = st.sidebar.date_input(
            "Выберите период предсказания",
            (period_start, period_end),
            format="MM.DD.YYYY",
        )
        if k:  # если данные выбраны
            start_date_n, end_date_n = k
        name_model = f'{model_name}'
        params_model = {"model_name": name_model, "item_id": option, "start_date": start_date_n, "end_date": end_date_n}
        logger.debug(f"Start predict: {name_model}")
        prediction = await get_data(url=url_predict_price, params=params_model)
        df_predict = json_to_dataframe(prediction)
        df_predict['prediction_date'] = pd.to_datetime(df_predict['prediction_date'])
        df_predict_filtered = df_predict[
            (df_predict['prediction_date'].dt.date > start_date_n) & (
                        df_predict['prediction_date'].dt.date < end_date_n)]
        logger.debug(f"End predict: {name_model}")
        for i in atr:
            params_to_atr = params_to_atr = {"attribute_name": i, "ticker_id": option, "date_from": start_date,
                                             "date_to": end_date}
            res = await get_data(url=url_get_inference_attribute_values, params=params_to_atr)
            if res:
                data = json_to_dataframe(res)
                #  on='business_date'
                all_indicator_dfs = pd.concat([all_indicator_dfs, data])
        logger.info(f"Start visualization")
        if all_indicator_dfs.empty:
            plot_data(df)
        else:
            plot_data(df, all_indicator_dfs, df_predict_filtered)
        logger.info(f"End visualization")
        with st.expander("Расширенный анализ данных", expanded=False):
            st.subheader('Гистограмма распределения признака')
            numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            col_hist = st.selectbox('Выберите признак для гистограммы', [''] + numerical_cols)
            if col_hist:
                if col_hist != '':
                    fig = px.histogram(df, x=col_hist, title=f'Распределение {col_hist}')
                    st.plotly_chart(fig)
            st.subheader('Диаграмма размаха')
            col_boxplot = st.selectbox('Выберите признак для boxplot', [''] + numerical_cols)
            if col_boxplot:
                if col_boxplot != '':
                    fig = px.box(df, y=col_boxplot, title=f'Диаграмма размаха для {col_boxplot}')
                    st.plotly_chart(fig)

            st.subheader('Корреляционная матрица')
            if not all_indicator_dfs.empty and 'business_date' in df.columns:
                # Разворачиваем индикаторы в отдельные столбцы
                all_indicator_dfs_pivot = all_indicator_dfs.pivot_table(
                    index='business_date', columns='attribute_name', values='value'
                ).reset_index()
                # Объединяем с данными по ценам
                merged_df = pd.merge(df[['business_date', 'close']], all_indicator_dfs_pivot,
                                     on='business_date', how='inner')

                # Вычисляем корреляционную матрицу
                numerical_cols_merged = merged_df.select_dtypes(include=['int64', 'float64']).columns.tolist()
                corr_matrix = merged_df[numerical_cols_merged].corr()
                # Визуализация
                fig = px.imshow(corr_matrix,
                                labels=dict(x="Признаки", y="Признаки", color="Корреляция"),
                                x=numerical_cols_merged,
                                y=numerical_cols_merged,
                                title="Корреляционная матрица")
                st.plotly_chart(fig)
        with st.expander("Предсказанные значения", expanded=False):
            if not df_predict_filtered.empty:
                st.write(df_predict_filtered)
            else:
                st.warning('Выберите модель или другую дату предсказания')
        with st.expander("Описательная статистика", expanded=False):
            st.dataframe(df.describe().T, width=800)
        logger.debug("End application")
    asyncio.run(zap(flag))


    # обучение происходит на бэке, мы отправляем модель прямиком туда
    async def post_data(url, payload):
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    try:
                        return await resp.json()
                    except:
                        return {"error": f"JSON parse error: {await resp.text()}"}
                else:
                    return {"error": f"Status {resp.status}: {await resp.text()}"}

    if flag == 2:
        csv_bytes = st.session_state.data.to_csv(index=False).encode("utf-8")
        encoded_data = base64.b64encode(csv_bytes).decode("utf-8")
        upload_url = "http://127.0.0.1:8000/api/v1/data/upload_cleaned_df"
        payload = {"data_base64": encoded_data}
        response = asyncio.run(post_data(upload_url, payload))
        # st.write("Ответ сервера:", response)

        # Блок обучения новой модели
        st.subheader("Обучение новой модели")
        model_name = st.text_input("Название модели", value="my_new_model")
        shift_days = st.number_input("Сдвиг (shift_days)", min_value=1, value=20)
        test_len = st.number_input("Размер тестовой выборки", min_value=1, value=50)
        ticker_name = st.text_input("Тикер для фильтрации", value="BZ=F")

        async def post_request(url, json_payload=None):
            import aiohttp
            json_payload = json_payload or {}
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=json_payload) as resp:
                    if resp.status == 200:
                        try:
                            return await resp.json()
                        except Exception:
                            return {"error": "JSON parse error", "raw": await resp.text()}
                    return {"error": f"Status {resp.status}", "detail": await resp.text()}


        if st.button("Обучить модель"):
            train_url = "http://127.0.0.1:8000/api/v1/model/train_new_model"
            payload = {
                "model_name": model_name,
                "shift_days": shift_days,
                "test_len": test_len,
                "ticker_name": ticker_name
            }
            result = asyncio.run(post_request(train_url,payload))
            st.write(f"Модель успешно обучена:")
            st.write(pd.DataFrame([result["model_stat"]]))
            plot_actual_vs_predicted(*result["train_test_result"].values())

            residual_train = (np.array(result["train_test_result"]["y_train"]) - np.array(result["train_test_result"]["y_train_pred"])).tolist()
            residual_test =  (np.array(result["train_test_result"]["y_test"]) - np.array(result["train_test_result"]["y_test_pred"])).tolist()
            plot_residual_analysis(residual_train, residual_test)


        if st.button("Обновить список моделей"):
            url_list = "http://127.0.0.1:8000/api/v1/model/list_models"
            model_list_data = asyncio.run(get_data(url_list))
            df_model = pd.DataFrame(model_list_data).dropna(subset=['model_name'])
            st.session_state['available_models'] = [x for x in df_model['model_name'] if x is not None and x !='']
