import streamlit as st
import pandas as pd

# Кэшируем данные
@st.cache_data
def load_data(file):
    return pd.read_csv(file, sep=';')

def run(data):
    # Дописать проверку на соответствие со столбцами
    df_csv = load_data(data)
    required_columns = ['close', 'business_date', 'ticker', 'open', 'high', 'low', 'adj_close', 'volume']
    if all(column in df_csv.columns for column in required_columns):
        st.session_state.data = df_csv  # Сохраняем данные в session_state
        return 2
    else:
        st.title(':blue[Команда 27. "Предсказание движения цен на фьючерсы на основе текстовых данных"]')
        st.warning('### Загруженный CSV-файл не содержит нужные столбцы. ###')
        st.write(
            'Пожалуйста, загрузите CSV-файл со следующими названиями столбцов: "close", "business_date", "ticker", "open", "high", "low", "adj_close", "volume"')
        st.session_state.data = None
        return 0

