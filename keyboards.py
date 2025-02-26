import random
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

# — Приветственное меню (После /start):
def start_menu():
    keyboard = [
        [KeyboardButton(text="проверить интуицию")],
        [KeyboardButton(text="сейчас не до игр")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


# — Клавиатура после прохождения теста
def after_test_menu():
    keyboard = [
        [KeyboardButton(text="результаты"), KeyboardButton(text="обои")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


# — Клавиатура для выбора обоев
def wallpapers_menu():
    keyboard = [
        [KeyboardButton(text="обои1"), KeyboardButton(text="обои2")],
        [KeyboardButton(text="обои3"), KeyboardButton(text="обои4")],
        [KeyboardButton(text="в начало")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


# — Клавиатура после выбора обоев
def wallpaper_download_menu():
    keyboard = [
        [KeyboardButton(text="скачать ещё"), KeyboardButton(text="в начало")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def generate_answers_keyboard(correct_answer: str, answers: list):
    """
    Генерация клавиатуры с 4 ответами + кнопка "в начало".
    answers: ['Answer1', 'Answer2', 'Answer3'] без correct
    correct_answer: 'Correct'
    
    Итог: 4 варианта (включая correct), расположенные рандомно,
    + 5-я кнопка "в начало" всегда снизу.
    """
    all_answers = answers + [correct_answer]
    random.shuffle(all_answers)  # перемешиваем 4 варианта

    # Создаём раскладку 2x2 для 4 ответов
    # Пример: [ans1, ans2]
    #         [ans3, ans4]
    keyboard_layout = []
    row = []
    for i, ans in enumerate(all_answers, start=1):
        row.append(KeyboardButton(text=ans))
        if i % 2 == 0:
            keyboard_layout.append(row)
            row = []
    # Возможно, если вариантов 4 — у нас 2 ряда; row уже пустой

    # Добавляем кнопку "в начало"
    keyboard_layout.append([KeyboardButton(text="в начало")])

    return ReplyKeyboardMarkup(keyboard=keyboard_layout, resize_keyboard=True)

def final_inline_keyboard():
    """
    Финальный экран: In-line кнопки [Ссылка][в начало]
    """
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Ссылка", url="https://google.com"),
            InlineKeyboardButton(text="В начало", callback_data="go_to_start")
        ]
    ])
    return markup

def results_inline_keyboard():
    """
    Кнопка [Ссылка] для результатов.
    """
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Ссылка", url="https://google.com")
        ]
    ])
    return markup
