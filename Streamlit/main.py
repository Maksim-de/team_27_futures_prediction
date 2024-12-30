import streamlit as st
import pandas as pd


# Кэшируем данные
@st.cache_data
def load_data(file):
    return pd.read_csv(file)


def main():
    # Настройка страницы
    st.set_page_config(page_title='Команда 27', page_icon='📈')

    # # Настройка сайдебара слева
    # st.sidebar.title('Загрузка датасета')
    # data = st.sidebar.file_uploader("**Загрузите CSV-файл**", type=["csv"])
    # if data is not None:
    #     #Дописать проверку на соответствие со столбцами
    #     df = load_data(data)
    #     st.session_state.data = df  # Сохраняем данные в session_state
    # else:
    #     st.warning('### Загрузите CSV-файл в левом окошке ###')

    # Навигация
    st.sidebar.title('Навигация')
    page = st.sidebar.radio('Выберите страницу:',
                            ['Описание', 'EDA + предикт', 'Новости'])

    if page == 'Описание':
        import page1
        page1.run()
    elif page == 'EDA + предикт':
        import EDA_page
        EDA_page.run()
    elif page == 'Новости':
        import news
        news.run()


# elif page == 'Модель с выбором':
#     import page3
#     page3.run()


if __name__ == "__main__":
    main()
