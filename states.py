from aiogram.fsm.state import State, StatesGroup

class BotStates(StatesGroup):
    MAIN_MENU = State()           # Главное меню
    QUIZ = State()                # Прохождение викторины
    WALLPAPER_CHOOSE = State()    # Выбор обоев
    WALLPAPER_DOWNLOAD = State()  # Загрузка/скачивание обоев
