from handler import *
import plotly.graph_objects as go
import datetime

API_URL = 'http://127.0.0.1:8000/api/v1'
url_get_news = API_URL + '/data/get_news_sentiment'
get_data_status = API_URL + '/data/get_data_status'


def plot_data(df, indicators_df=None):
    if df.empty:
        st.warning("Нет данных для отображения графика.")
        return

    # Преобразование business_date в тип datetime, если это не так
    df['business_date'] = pd.to_datetime(df['business_date'])

    # Сортировка DataFrame по дате
    df = df.sort_values(by='business_date')

    fig = None  # Инициализация фигуры для дальнейшего использования
    fig = go.Figure(data=[go.Scatter(x=df['business_date'], y=df['avg_finbert_sentiment'], mode='lines', name='Цена')])
    fig.update_layout(title='Линейный график sentiment',
                      xaxis_title='Дата',
                      yaxis_title='avg_finbert_sentiment')

    main_chart_container = st.container()  # Создаем контейнер для основного графика
    if fig:
        with main_chart_container:  # Выводим основной график в контейнере
            st.plotly_chart(fig)


def run():
    st.header('')
    tickers = ['CL=F', 'BZ=F', 'SPY', 'QQQ']
    option = st.sidebar.selectbox('Выберите тикер', tickers)
    today = datetime.datetime.now()
    last_year = today.year - 1
    last_date = datetime.date(last_year, 1, 1)

    d = st.sidebar.date_input(
        "Выберите даты",
        (last_date, today),
        max_value=today,
        format="MM.DD.YYYY",
    )

    if d:  # если данные выбраны
        start_date, end_date = d

        # Проверка, что start_date и end_date выбраны
        if start_date is None or end_date is None:
            st.error("Ошибка: Выберите начальную и конечную даты.")
        # Проверка, что end_date не меньше start_date
        elif end_date < start_date:
            st.error("Ошибка: Конечная дата не может быть меньше начальной даты.")
        else:
            params = {"ticker_id": option, "date_from": start_date, "date_to": end_date}

            async def zap():
                result_fit = await get_data(url_get_news, params)
                result2 = await get_data(url=get_data_status, params='')
                st.dataframe(result2)
                df = json_to_dataframe(result_fit)
                plot_data(df)

            asyncio.run(zap())
