import streamlit as st
import pandas as pd
import aiohttp
import asyncio
import json
from urllib.parse import urlencode
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots

API_URL = 'http://127.0.0.1:8000/api/v1'
url_download_prices = API_URL + '/data/get_price_table'
url_list_atributes = API_URL + '/model/list_inference_attributes'
url_get_inference_attribute_values = API_URL + '/model/get_inference_attribute_values'
url_get_list_model = API_URL + '/model/list_models'
url_predict_price = API_URL + '/model/predict_price'

async def get_data(url, params = None):
    async with aiohttp.ClientSession() as session:
        if (params is not None) or params!= '':
            full_url = f"{url}?{urlencode(params)}"  # Добавляем параметры к URL
        else:
            full_url = url
        async with session.get(full_url) as response:
            if response.status == 200:
                try:
                    return await response.json()
                except json.JSONDecodeError:
                    return await response.text()
            else:
                return {"error": f"Ошибка {response.status} : {await response.text()}"}

# def json_to_dataframe(json_data):
#     """
#     Преобразует JSON в Pandas DataFrame.
#
#     Args:
#         json_data: JSON строка или словарь.
#
#     Returns:
#         Pandas DataFrame или None при ошибке.
#     """
#     try:
#         if isinstance(json_data, str):
#             data = json.loads(json_data)
#         elif isinstance(json_data, dict):
#             data = json_data
#         else:
#             return None  # Обработка неподходящего типа данных
#
#         if "data" not in data:
#             return None  # Обработка отсутствия ключа "data"
#
#         data_list = data["data"]
#
#         # Проверка данных и преобразование, если список не пустой
#         if data_list:
#             # Создаем список словарей для каждого элемента. Важно обработать нестандартные значения ключей
#             list_of_dicts = []
#             for i, item in enumerate(data_list):
#                 dict_item = {}
#                 for key, value in item.items():
#                     dict_item[key] = value
#                 list_of_dicts.append(dict_item)
#
#
#             df = pd.DataFrame(list_of_dicts)
#             return df
#         else:
#            return pd.DataFrame()  # Возвращаем пустой DataFrame если "data" пустой
#
#
#     except (json.JSONDecodeError, KeyError, ValueError) as e:
#         print(f"Ошибка при парсинге JSON или формировании DataFrame: {e}")
#         return None

def json_to_dataframe(json_data):
    """
    Преобразует JSON в Pandas DataFrame.

    Args:
        json_data: JSON строка, список словарей или словарь.

    Returns:
        Pandas DataFrame или None при ошибке.
    """
    try:
        if isinstance(json_data, str):
            data = json.loads(json_data)
        elif isinstance(json_data, dict):
            data = json_data
        elif isinstance(json_data, list):  # добавлена обработка list
            data = json_data
        else:
            return None  # Обработка неподходящего типа данных

        if isinstance(data, dict):
            if "data" not in data:
                return None  # Обработка отсутствия ключа "data"
            data_list = data["data"]
        elif isinstance(data, list):
            data_list = data  # если data является list то присваиваем этот list
        else:
            return None  # не обрабатываемый случай

        # Проверка данных и преобразование, если список не пустой
        if data_list:
            # Создаем список словарей для каждого элемента. Важно обработать нестандартные значения ключей
            list_of_dicts = []
            for item in data_list:
                if isinstance(item, dict):  # добавлена проверка
                    dict_item = {}
                    for key, value in item.items():
                        dict_item[key] = value
                    list_of_dicts.append(dict_item)

            if list_of_dicts:
                df = pd.DataFrame(list_of_dicts)
                return df
            else:
                return pd.DataFrame()  # Возвращаем пустой DataFrame если список list_of_dicts пустой
        else:
            return pd.DataFrame()  # Возвращаем пустой DataFrame если "data" пустой

    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Ошибка преобразования JSON в DataFrame: {e}")
        return None

# def plot_data(df):
#     """
#     Отображает график цены (линейный или свечной) в Streamlit.
#
#     Args:
#         df: Pandas DataFrame с данными о цене (должен содержать колонки 'business_date', 'open', 'high', 'low', 'close').
#     """
#
#     st.header("График цены")
#
#     if df.empty:
#         st.warning("Нет данных для отображения графика.")
#         return
#
#     # Преобразование business_date в тип datetime, если это не так
#     df['business_date'] = pd.to_datetime(df['business_date'])
#
#     # Сортировка DataFrame по дате
#     df = df.sort_values(by='business_date')
#
#     chart_type = st.radio("Выберите тип графика", ["Линейный", "Свечной"])
#
#     if chart_type == "Линейный":
#         fig = go.Figure(data=[go.Scatter(x=df['business_date'], y=df['close'], mode='lines')])
#         fig.update_layout(title='График цены закрытия',
#                           xaxis_title='Дата',
#                           yaxis_title='Цена закрытия')
#         st.plotly_chart(fig)
#
#     elif chart_type == "Свечной":
#         fig = go.Figure(data=[go.Candlestick(x=df['business_date'],
#                                              open=df['open'],
#                                              high=df['high'],
#                                              low=df['low'],
#                                              close=df['close'])])
#         fig.update_layout(title='Свечной график цены',
#                           xaxis_title='Дата',
#                           yaxis_title='Цена')
#         st.plotly_chart(fig)


# def plot_data(df, indicators_df=None):
#     if df.empty:
#         st.warning("Нет данных для отображения графика.")
#         return
#
#     # Преобразование business_date в тип datetime, если это не так
#     df['business_date'] = pd.to_datetime(df['business_date'])
#
#     # Сортировка DataFrame по дате
#     df = df.sort_values(by='business_date')
#
#     chart_type = st.radio("Выберите тип графика", ["Линейный", "Свечной"], key="chart_type_radio")
#
#     fig = None  # Инициализация фигуры для дальнейшего использования
#     if chart_type == "Линейный":
#         fig = go.Figure(data=[go.Scatter(x=df['business_date'], y=df['close'], mode='lines', name='Цена')])
#         fig.update_layout(title='График цены закрытия',
#                           xaxis_title='Дата',
#                           yaxis_title='Цена закрытия')
#
#
#     elif chart_type == "Свечной":
#         fig = go.Figure(data=[go.Candlestick(x=df['business_date'],
#                                              open=df['open'],
#                                              high=df['high'],
#                                              low=df['low'],
#                                              close=df['close'], name='Цена')])
#         fig.update_layout(title='Свечной график цены',
#                           xaxis_title='Дата',
#                           yaxis_title='Цена')
#
#     main_chart_container = st.container()  # Создаем контейнер для основного графика
#
#     if indicators_df is not None and not indicators_df.empty:
#         indicators_df['business_date'] = pd.to_datetime(indicators_df['business_date'])
#         indicators_df = indicators_df.sort_values(by='business_date')
#         separate_indicators = ["ATR", "BB_lower", "BB_middle", "BB_upper",
#                                "CCI", "MACD", "MACD_Signal", "MOM",
#                                "ROC", "rsi", "Stochastic_D",
#                                "Stochastic_K", "volume", "Williams_R"]
#
#         indicators_to_add_main = {}  # Изменен на словарь
#
#         for attr_name in indicators_df['attribute_name'].unique():
#             indicator_data = indicators_df[indicators_df['attribute_name'] == attr_name]
#
#             if attr_name in separate_indicators:
#                 # Создаем отдельный график для индикаторов из списка separate_indicators
#                 st.header(f"График индикатора {attr_name}")
#                 indicator_fig = go.Figure(data=[
#                     go.Scatter(x=indicator_data['business_date'], y=indicator_data['value'], mode='lines',
#                                name=attr_name)])
#                 indicator_fig.update_layout(title=f'График индикатора {attr_name}',
#                                             xaxis_title='Дата',
#                                             yaxis_title='Значение')
#                 st.plotly_chart(indicator_fig)
#
#             else:
#                 # Собираем индикаторы, которые нужно добавить на основной график
#                 indicators_to_add_main[attr_name] = indicator_data # Сохраняем dataframe
#
#         if indicators_to_add_main and fig:
#              for attr_name, indicator_data in indicators_to_add_main.items(): # Проходим по словарю
#                 fig.add_trace(go.Scatter(x=indicator_data['business_date'], y=indicator_data['value'], mode='lines',
#                                      name=attr_name)) # Теперь добавляем весь DataFrame за раз
#     if fig:
#         with main_chart_container:  # Выводим основной график в контейнере
#             st.plotly_chart(fig)

def plot_data(df, indicators_df=None, predicted_df=None):
    if df.empty:
        st.warning("Нет данных для отображения графика.")
        return
    df['business_date'] = pd.to_datetime(df['business_date'])

    df = df.sort_values(by='business_date')

    chart_type = st.radio("Выберите тип графика", ["Линейный", "Свечной"], key="chart_type_radio")

    fig = None  # Инициализация фигуры для дальнейшего использования
    if chart_type == "Линейный":
        fig = go.Figure(data=[go.Scatter(x=df['business_date'], y=df['close'], mode='lines', name='Цена')])
        fig.update_layout(title='График цены закрытия',
                          xaxis_title='Дата',
                          yaxis_title='Цена закрытия')


    elif chart_type == "Свечной":
        fig = go.Figure(data=[go.Candlestick(x=df['business_date'],
                                             open=df['open'],
                                             high=df['high'],
                                             low=df['low'],
                                             close=df['close'], name='Цена')])
        fig.update_layout(title='Свечной график цены',
                          xaxis_title='Дата',
                          yaxis_title='Цена')

    main_chart_container = st.container()  # Создаем контейнер для основного графика

    if indicators_df is not None and not indicators_df.empty:
        indicators_df['business_date'] = pd.to_datetime(indicators_df['business_date'])
        indicators_df = indicators_df.sort_values(by='business_date')
        separate_indicators = ["ATR", "BB_lower", "BB_middle", "BB_upper",
                               "CCI", "MACD", "MACD_Signal", "MOM",
                               "ROC", "rsi", "Stochastic_D",
                               "Stochastic_K", "volume", "Williams_R"]

        indicators_to_add_main = {}  # Изменен на словарь

        for attr_name in indicators_df['attribute_name'].unique():
            indicator_data = indicators_df[indicators_df['attribute_name'] == attr_name]

            if attr_name in separate_indicators:
                # Создаем отдельный график для индикаторов из списка separate_indicators
                st.header(f"График индикатора {attr_name}")
                indicator_fig = go.Figure(data=[
                    go.Scatter(x=indicator_data['business_date'], y=indicator_data['value'], mode='lines',
                               name=attr_name)])
                indicator_fig.update_layout(title=f'График индикатора {attr_name}',
                                            xaxis_title='Дата',
                                            yaxis_title='Значение')
                st.plotly_chart(indicator_fig)

            else:
                indicators_to_add_main[attr_name] = indicator_data  # Сохраняем dataframe

        if indicators_to_add_main and fig:
            for attr_name, indicator_data in indicators_to_add_main.items():  # Проходим по словарю
                fig.add_trace(go.Scatter(x=indicator_data['business_date'], y=indicator_data['value'], mode='lines',
                                         name=attr_name))  # Теперь добавляем весь DataFrame за раз
    if predicted_df is not None and not predicted_df.empty:
        predicted_df['business_date'] = pd.to_datetime(predicted_df['prediction_date'])
        predicted_df = predicted_df.sort_values(by='prediction_date')

        if fig:
            fig.add_trace(go.Scatter(x=predicted_df['prediction_date'], y=predicted_df['prediction_value'], mode='lines',
                                     name='Предсказанное значение'))

    if fig:
        with main_chart_container:  # Выводим основной график в контейнере
            st.plotly_chart(fig)