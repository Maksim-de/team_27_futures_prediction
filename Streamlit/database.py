import streamlit as st
import pandas as pd
import aiohttp
import asyncio

API_URL = 'http://127.0.0.1:8000/api/v1'
url_download_prices = API_URL + '/data/get_price_table'

async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                st.error(f"Ошибка получения данных: {response.status}")
                return None

def json_to_dataframe(data):
    return pd.DataFrame.from_dict(data, orient='columns')  # Возвращаем пустой DataFrame в случае ошибки


def print_data(df):
    '''
    Функция, которая выводит датасет с определенным количеством строк
    '''
    # Ввод числа
    if st.checkbox('Использовать выпадающий список для вывода строк'):
        num_rows = st.selectbox("Выберите количество строк для отображения:", options=list(range(1, len(df) + 1)),
                                index=2)
        st.write(f"Выводим {num_rows} строк:")
        st.dataframe(df.head(num_rows))

    if st.checkbox('Использовать ползунок для вывода строк'):
        num_rows = st.slider("Выберите количество строк для отображения", min_value=1, max_value=len(df), value=5)
        st.write(f"Выводим {num_rows} строк:")
        st.dataframe(df.head(num_rows))


def run():
    st.title(':blue[Команда 27. "Предсказание движения цен на фьючерсы на основе текстовых данных"]')
    df = ''

    st.header('Полученный датасет из БД')
    print_data(df)
