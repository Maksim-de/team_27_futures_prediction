import streamlit as st
import pymysql
import pandas as pd

@st.cache_data
def download():
    st.header('Загружаем данные из БД')
    host = 'mysql.7e38bf8aa2a7.hosting.myjino.ru'
    username = 'j06500307'
    password = 'Gvw88YdWw'
    database_name = 'j06500307'

    connection = pymysql.connect(host=host,
                                 user=username,
                                 password=password,
                                 database=database_name)

    # Параметры для выборки
    batch_size = 3000
    offset = 0
    all_data = []

    # Определяем общее количество записей для расчета прогресса
    total_query = "SELECT COUNT(*) FROM news_data"
    total_records = pd.read_sql(total_query, connection).iloc[0, 0]
    total_batches = (total_records // batch_size) + (1 if total_records % batch_size > 0 else 0)

    # Создаем прогресс-бар
    progress_bar = st.progress(0)

    while True:
        query = f"SELECT * FROM news_data LIMIT {batch_size} OFFSET {offset}"
        df_small = pd.read_sql(query, connection)
        if df_small.empty:
            break
        all_data.append(df_small)
        offset += batch_size

        # Обновляем прогресс-бар
        progress_percentage = (offset // batch_size) / total_batches
        progress_bar.progress(progress_percentage)

    df = pd.concat(all_data, ignore_index=True)

    # Удалим столбцы thread_uuid, post_uuid	и request_id
    del df['thread_uuid']
    del df['post_uuid']
    del df['request_id']
    del df['news_provider']
    st.session_state = df

def run():
    df = st.session_state
    if st.checkbox('Заполняем пропуски в переменной "country"'):
        df.loc[df['country'] == '', 'country'] = 'Global'
        df['country'] = df['country'].fillna(value='Global')

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

    st.session_state = df
