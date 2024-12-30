import pandas as pd
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

logger = setup_logger("EDA")
def run():

    logger.debug("Starting application")
    st.header('Анализ данных и прогнозирование')
    tickers = ['CL=F', 'BZ=F', 'SPY', 'QQQ']
    option = st.sidebar.selectbox('Выберите тикер', tickers)
    today = datetime.datetime.now()
    last_year = today.year - 1
    last_date = datetime.date(last_year, 1, 1)
    next_week = today + datetime.timedelta(days=7)
    last_week = today - datetime.timedelta(days=7)

    d = st.sidebar.date_input(
        "Выберите период",
        (last_date, today),
        max_value = today,
        format="MM.DD.YYYY",
    )
    if d:  # если данные выбраны
        start_date, end_date = d
        logger.info(f"Selected date range: {start_date} - {end_date}")
    if option:
        params = {"ticker_id": option, "date_from": start_date, "date_to": end_date}
        async def zap():
            logger.debug(f"Starting data fetching for ticker: {option}")
            df_csv = st.session_state
            if df_csv is not None:
                results = await asyncio.gather(
                    get_data(url_download_prices, params),
                    get_data(url_list_atributes, params=''),
                    get_data(url_get_list_model, params='')
                )
                result_fit, option_indicators, option_model = results
                df = json_to_dataframe(result_fit)
            else:
                results = await asyncio.gather(
                    get_data(url_list_atributes, params=''),
                    get_data(url_get_list_model, params='')
                )
                option_indicators, option_model = results
                result_fit = df

            logger.debug(f"End json_to_dataframe download price: {option}")
            atr = st.sidebar.multiselect('Доступные показатели', option_indicators, default = 'sma')
            all_indicator_dfs = pd.DataFrame()
            df_model = json_to_dataframe(option_model)
            logger.debug(f"End json_to_dataframe option model: {option}")
            st.sidebar.write('Выбор модели для предсказания')
            model_name = st.sidebar.selectbox('Доступные модели', df_model['model_name'])
            k = st.sidebar.date_input(
                "Выберите период",
                (last_week, next_week),
                format="MM.DD.YYYY",
            )
            if k:  # если данные выбраны
                start_date_n, end_date_n = k
            name_model = f'{model_name}.pkl'
            params_model = {"model_name": name_model, "item_id": option, "start_date": start_date_n, "end_date": end_date_n}
            logger.debug(f"Start predict: {name_model}")
            prediction = await get_data(url=url_predict_price, params=params_model)
            df_predict = json_to_dataframe(prediction)
            df_predict['prediction_date'] = pd.to_datetime(df_predict['prediction_date'])
            df_predict_filtered = df_predict[
                (df_predict['prediction_date'].dt.date > start_date_n) & (df_predict['prediction_date'].dt.date < end_date_n)]
            logger.debug(f"End predict: {name_model}")
            for i in atr:
                params_to_atr = params_to_atr = {"attribute_name": i,"ticker_id": option, "date_from": start_date, "date_to": end_date}
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

        asyncio.run(zap())
