import streamlit as st

# Навигация
def navigation():
    st.sidebar.title('Навигация')
    page = st.sidebar.radio('Выберите страницу:',
                            ['Описание', 'EDA + предикт', 'Новости'], index=None)
    if page == 'Описание':
        import page1
        page1.run()
    elif page == 'EDA + предикт':
        import EDA_page
        EDA_page.run()
    elif page == 'Новости':
        import news
        news.run()

def main():
    # Настройка страницы
    st.set_page_config(page_title='Команда 27', page_icon='📈')
    # Настройка сайдебара слева
    st.sidebar.title('Загрузка датасета')
    upload_option = st.sidebar.radio('Выберите вариант загрузки:',
                                     ['Из базы данных', 'Загрузка CSV-файла'], index=None)

    flag = 0
    if upload_option == 'Из базы данных':
        import database
        database.run()
        flag = 1
    elif upload_option == 'Загрузка CSV-файла':
        data = st.sidebar.file_uploader("**Загрузите CSV-файл**", type=["csv"])
        if data is not None:
            import database_csv
            database_csv.run(data)
            flag = 1
        else:
            st.title(':blue[Команда 27. "Предсказание движения цен на фьючерсы на основе текстовых данных"]')
            st.warning('### Загрузите CSV-файл в левом окошке ###')
    else:
        st.title(':blue[Команда 27. "Предсказание движения цен на фьючерсы на основе текстовых данных"]')
        st.warning('### Выберете слева способ загрузки датасета ###')

    if flag == 1:
        navigation()

if __name__ == "__main__":
    main()
