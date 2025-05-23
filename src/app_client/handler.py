import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import aiohttp
import asyncio
import json
from urllib.parse import urlencode
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots

API_URL = 'http://predict_api:8000/api/v1'
#API_URL = 'http://127.0.0.1:8000/api/v1'
url_download_prices = API_URL + '/data/get_price_table'
url_list_atributes = API_URL + '/model/list_inference_attributes'
url_get_inference_attribute_values = API_URL + '/model/get_inference_attribute_values'
url_get_list_model = API_URL + '/model/list_models'
url_predict_price = API_URL + '/model/predict_price'

async def get_data(url, params=None):
    async with aiohttp.ClientSession() as session:
        # Проверяем, что params - это словарь (или None)
        if params and isinstance(params, dict):
            full_url = f"{url}?{urlencode(params)}"
        else:
            # Если params нет или он не словарь, просто не добавляем query
            full_url = url

        async with session.get(full_url) as response:
            if response.status == 200:
                try:
                    return await response.json()
                except:
                    # может быть текст
                    return await response.text()
            else:
                return {"error": f"Ошибка {response.status} : {await response.text()}"}

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
        indicators_to_add_main = {}
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

def plot_actual_vs_predicted(
        dates_train,
        y_train,
        y_train_pred,
        dates_test,
        y_test,
        y_test_pred,
        ticker_name
):
    """
    Выводим линии факта и прогноз полученные после обучения новой модели
    """

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates_train, y=y_train,
        mode='lines', line=dict(color='blue', dash='dot'),
        name='Actual train change'
    ))
    fig.add_trace(go.Scatter(
        x=dates_train, y=y_train_pred,
        mode='lines', line=dict(color='blue'),
        name='Predicted train change'
    ))

    fig.add_trace(go.Scatter(
        x=dates_test, y=y_test,
        mode='lines', line=dict(color='orange', dash='dot'),
        name='Actual test change'
    ))
    fig.add_trace(go.Scatter(
        x=dates_test, y=y_test_pred,
        mode='lines', line=dict(color='orange'),
        name='Predicted test change'
    ))

    fig.update_layout(
        title=f"Actual vs Predicted Values for {ticker_name}",
        xaxis=dict(
            title="Date",
            showgrid=True,
            gridcolor='lightgray',
            tickformat='%Y-%m-%d',
            dtick="M7",
            tickangle=45,
            tickmode="auto"
        ),
        yaxis=dict(
            title="Price Change",
            showgrid=True,
            gridcolor='lightgray'
        ),
        # legend=dict(
        #     title="Legend",
        #     orientation="h",
        #     yanchor="bottom",
        #     y=1.02,
        #     xanchor="right",
        #     x=1
        # ),
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=40)
    )

    st.plotly_chart(fig)

def plot_residual_analysis(residual_train, residual_test):
    """
    Отображает распределения остатков и Q-Q графики для тренировочных и тестовых данных.
    """

    # Подготовка данных для распределения остатков (гистограммы с KDE)
    hist_data_train = [residual_train]
    hist_data_test = [residual_test]
    group_labels_train = ['Train Residuals']
    group_labels_test = ['Test Residuals']

    # Создание гистограммы с KDE для тренировочных остатков
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Train Residuals Distribution",
            "Train Residuals Q-Q Plot",
            "Test Residuals Distribution",
            "Test Residuals Q-Q Plot"
        ),
        horizontal_spacing=0.15,
        vertical_spacing=0.15,
    )

    # Гистограмма для тренировочных остатков
    hist_train, bin_edges_train = np.histogram(residual_train, bins=30, density=True)
    kde_train = stats.gaussian_kde(residual_train)
    x_train_kde = np.linspace(min(residual_train), max(residual_train), 100)
    y_train_kde = kde_train(x_train_kde)
    fig.add_trace(
        go.Bar(x=bin_edges_train[:-1], y=hist_train, name='Train Residuals', marker_color='blue'),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=x_train_kde, y=y_train_kde, mode='lines', name='Train KDE', line=dict(color='blue')),
        row=1, col=1
    )

    # Q-Q Plot для тренировочных остатков
    qq_train = stats.probplot(residual_train, dist="norm")
    fig.add_trace(
        go.Scatter(x=qq_train[0][0], y=qq_train[0][1], mode='markers', name='Train Q-Q', marker_color='blue'),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=qq_train[0][0], y=qq_train[0][0], mode='lines', name='Ideal Line', line=dict(color='red')),
        row=1, col=2
    )

    # Гистограмма для тестовых остатков
    hist_test, bin_edges_test = np.histogram(residual_test, bins=30, density=True)
    kde_test = stats.gaussian_kde(residual_test)
    x_test_kde = np.linspace(min(residual_test), max(residual_test), 100)
    y_test_kde = kde_test(x_test_kde)
    fig.add_trace(
        go.Bar(x=bin_edges_test[:-1], y=hist_test, name='Test Residuals', marker_color='orange'),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=x_test_kde, y=y_test_kde, mode='lines', name='Test KDE', line=dict(color='orange')),
        row=2, col=1
    )

    # Q-Q Plot для тестовых остатков
    qq_test = stats.probplot(residual_test, dist="norm")
    fig.add_trace(
        go.Scatter(x=qq_test[0][0], y=qq_test[0][1], mode='markers', name='Test Q-Q', marker_color='orange'),
        row=2, col=2
    )
    fig.add_trace(
        go.Scatter(x=qq_test[0][0], y=qq_test[0][0], mode='lines', name='Ideal Line', line=dict(color='red')),
        row=2, col=2
    )

    # Настройка оформления
    fig.update_layout(
        title_text="Residual Analysis",
        showlegend=False,
        height=800,
        width=1000,
        template="plotly_white"
    )

    st.plotly_chart(fig)