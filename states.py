from aiogram.fsm.state import State, StatesGroup

class StartState(StatesGroup):
    waiting_for_action = State()  # стартовый экран

class TestState(StatesGroup):
    question_in_progress = State()  # идёт прохождение теста

class WallpaperState(StatesGroup):
    choosing_wallpapers = State()
    download_wallpapers = State()
