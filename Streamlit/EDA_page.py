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



async def get_data(url, params):
    async with aiohttp.ClientSession() as session:
        full_url = f"{url}?{urlencode(params)}"  # Добавляем параметры к URL
        async with session.get(full_url) as response:
            if response.status == 200:
                try:
                    return await response.json()
                except json.JSONDecodeError:
                    return await response.text()
            else:
                return {"error": f"Ошибка {response.status} : {await response.text()}"}



def run():
    st.header('Анализ данных')
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
        # start_date_str = start_date.isoformat()
        # end_date_str = end_date.isoformat()
    if option:
        params = {"ticker_id": option, "date_from": start_date, "date_to": end_date}
        async def zap():
            result_fit = await get_data(url_download_prices, params)
            df = json_to_dataframe(result_fit)
            #plot_data(df)
            option_indicators = await get_data(url=url_list_atributes, params = '')
            atr = st.sidebar.multiselect('Доступные показатели', option_indicators, default = 'sma')
            all_indicator_dfs = pd.DataFrame()
            option_model = await get_data(url=url_get_list_model, params='')
            df_model = json_to_dataframe(option_model)
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
            prediction = await get_data(url=url_predict_price, params=params_model)
            df_predict = json_to_dataframe(prediction)
            df_predict['prediction_date'] = pd.to_datetime(df_predict['prediction_date'])
            df_predict_filtered = df_predict[
                (df_predict['prediction_date'].dt.date > start_date_n) & (df_predict['prediction_date'].dt.date < end_date_n)]
            for i in atr:
                params_to_atr = params_to_atr = {"attribute_name": i,"ticker_id": option, "date_from": start_date, "date_to": end_date}
                res = await get_data(url=url_get_inference_attribute_values, params=params_to_atr)
                if res:
                    data = json_to_dataframe(res)
                    #  on='business_date'
                    all_indicator_dfs = pd.concat([all_indicator_dfs, data])
            if all_indicator_dfs.empty:
                plot_data(df)
            else:
                plot_data(df, all_indicator_dfs, df_predict_filtered)

            with st.expander("Описательная статистика", expanded=False):
                st.dataframe(df.describe().T, width=800)
            st.write(df_predict_filtered)
        asyncio.run(zap())
