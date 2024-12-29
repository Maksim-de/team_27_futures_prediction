import streamlit as st
import pandas as pd

# Кэшируем данные
@st.cache_data
def load_data(file):
    return pd.read_csv(file)

def main():
    # Настройка страницы
    st.set_page_config(page_title='Команда 27', page_icon='📈')
    st.title(':blue[Команда 27. "Предсказание движения цен на фьючерсы на основе текстовых данных"]')

    # Настройка сайдебара слева
    st.sidebar.title('Загрузка датасета')
    upload_option = st.sidebar.radio('Выберите вариант загрузки:',
                                     ['Из базы данных', 'Загрузка CSV-файла'], index=None)
    flag = 0
    if upload_option == 'Из базы данных':
        # Дописать код
        import database
        database.download()
        database.run()
        flag = 1
    elif upload_option == 'Загрузка CSV-файла':
        data = st.sidebar.file_uploader("**Загрузите CSV-файл**", type=["csv"])
        if data is not None:
            #Дописать проверку на соответствие со столбцами
            df = load_data(data)
            st.session_state.data = df  # Сохраняем данные в session_state
            flag = 1
        else:
            st.warning('### Загрузите CSV-файл в левом окошке ###')
    else:
        # Описание проекта
        import page1
        page1.run()


    # Навигация
    if flag == 1:
        st.sidebar.title('Навигация')
        page = st.sidebar.radio('Выберите страницу:',
                                ['Демонстрация аналитики',
                                 'Модель с выбором'], index=None)

        # if page == 'Демонстрация аналитики':
            # import page2
            # page2.run()
        # elif page == 'Модель с выбором':
        #     import page3
        #     page3.run()





if __name__ == "__main__":
    main()
