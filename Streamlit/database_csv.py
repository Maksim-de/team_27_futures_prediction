from database import *

# Кэшируем данные
@st.cache_data
def load_data(file):
    return pd.read_csv(file)

def run(data):
    st.title(':blue[Команда 27. "Предсказание движения цен на фьючерсы на основе текстовых данных"]')
    # Дописать проверку на соответствие со столбцами
    st.header('Загруженный CSV-файл')
    df_csv = load_data(data)
    st.session_state.data = df_csv  # Сохраняем данные в session_state

    print_data(df_csv) # Функция из database