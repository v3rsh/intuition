from aiogram.fsm.state import State, StatesGroup

class BotState(StatesGroup):
    MAIN_MENU = State()   # Главное меню
    QUIZ = State()        # Режим викторины
    CHOOSE = State()      # Выбор обоев (мелкие)
    DOWNLOAD = State()    # Скачивание/отправка крупных обоев
    RESULT = State()      # Результат (когда прогресс=10)
