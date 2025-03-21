import streamlit as st

def run():
    st.header('Описание проекта')
    st.write(
        '''
        Проект нацелен на разработку и внедрение моделей машинного обучения, способных предсказывать изменения цен на 
        финансовые активы, такие как WTI, Brent, S&P 500 и Nasdaq-100, используя текстовую информацию: новости, отчёты 
        и аналитические материалы.
        '''
    )

    st.header('Описание данных')
    st.button('[Данные берем тут](https://docs.webz.io/reference/output)')
    st.write(
        '''
        _news_provider_ - Откуда берем данные (сайт).\n
        _site_ - Домен верхнего уровня сайта.\n
        _titel_ - Название темы.\n
        _published-timestamp_ - Дата / время публикации темы.\n
        _country_ - Страна происхождения статьи определяется ее доменом, поддоменом или разделом сайта. 
        Это определяется с помощью показателей страны в веб-адресе (например, *.co.fr) или путем анализа страны, 
        генерирующей наибольшее количество трафика.\n
        _perfomamce_score_ - Оценка вирусности выставляется только для сообщений в новостях и блогах. 
        Оценка варьируется в диапазоне от 0 до 10. Оценка 0 означает, что публикация не удалась - 
        ею редко делились или вообще не публиковали. Оценка 10 означает, что пост был "в огне" и им тысячи 
        раз делились на Facebook.\n
        _domain_rank_ - Рейтинг, определяющий популярность домена.\n
        _lannguage_ - Язык сообщения.\n
        _sentiment_ - Контекст настроения, связанный с человеком или организацией. 
        Возможные значения: положительное, отрицательное, нет.\n
        _article_text_ - Текст статьи.
        '''
    )

    st.header('Участники')
    st.write(
        '''
        * Куратор, Дмитрий Качкин - @KachkinDmitrii \n
        * Участник 1, Максим Архипов — @pirici_pip, Maksim-de\n
        * Участник 2, Алексей Казанцев — @kazantsev_alexey, Kazantsev-Alexey\n
        * Участник 3, Александр Павловский — @xpavlovsky, apavlovskii\n
        * Участник 4, Ксения Балицкая — @Ksesha0000, Kseniya-5\n
        '''
    )

    if st.checkbox('Показать дополнительную информацию'):
        st.header('Финансовые активы')
        st.write(
            '''
            **WTI** — это сорт нефти, который добывается в США, преимущественно в Техасе. 
            Он является одним из основных эталонов для определения цен на нефть на мировом рынке. 
            WTI характеризуется высокой чистотой и низким содержанием серы, что делает его привлекательным для переработки. 
            Цены на WTI часто используются как индикатор состояния нефтяного рынка и экономики в целом.\n
            **BRENT** — это один из основных эталонных сортов нефти, используемый для определения цен на 
            нефть на международном рынке. Он добывается в Северном море и служит важным индикатором для 
            оценки стоимости нефти в Европе и других регионах.\n
            **S&P500** — это фондовый индекс, который включает в себя 500 крупнейших компаний, зарегистрированных 
            на фондовых рынках США. Он считается одним из основных индикаторов 
            состояния американской экономики и финансовых рынков.\n
            **Nasdaq (National Association of Securities Dealers Automated Quotations)** — это американская фондовая биржа, 
            которая была основана в 1971 году. Она известна своей технологической направленностью и является одной 
            из крупнейших бирж в мире по рыночной капитализации.
            '''
        )
