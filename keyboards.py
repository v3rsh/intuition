import random
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

def main_menu_kb():
    """
    Главное меню: две кнопки
    [проверить интуицию]
    [сейчас не до игр]
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="проверить интуицию")],
            [KeyboardButton(text="сейчас не до игр")]
        ],
        resize_keyboard=True
    )

def dynamic_wallpapers_menu(button_texts: list[str]) -> ReplyKeyboardMarkup:
    """
    Из списка button_texts создаём клавиатуру:
    1 кнопка на строке + последняя строка "в начало".
    """
    keyboard_rows = [[KeyboardButton(text=text)] for text in button_texts]

    # Добавляем кнопку 'в начало' отдельной строкой
    keyboard_rows.append([KeyboardButton(text="в начало")])

    return ReplyKeyboardMarkup(keyboard=keyboard_rows, resize_keyboard=True)

def wallpapers_download_menu():
    """
    Для BotState.DOWNLOAD: [Выбрать другие обои] [в начало]
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Выбрать другие обои")],
            [KeyboardButton(text="в начало")]
        ],
        resize_keyboard=True
    )

def generate_quiz_answers(correct_answer: str, answers: list) -> ReplyKeyboardMarkup:
    """
    4 варианта (correct + 3 answers), перемешанные.
    5-я кнопка: в начало.
    """
    variants = answers + [correct_answer]
    random.shuffle(variants)

    # Клавиатура с ответами (одна кнопка в строке)
    keyboard_layout = [[KeyboardButton(text=ans)] for ans in variants]

    # Кнопка 'в начало' в отдельной строке
    keyboard_layout.append([KeyboardButton(text="в начало")])

    return ReplyKeyboardMarkup(
        keyboard=keyboard_layout,
        resize_keyboard=True
    )

def result_inline_keyboard():
    """
    Финальная inline-клавиатура (2 кнопки):
    [Ссылка] [в начало (callback_data='to_main')]
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Ссылка", url="https://example.com"),
                InlineKeyboardButton(text="в начало", callback_data="to_main")
            ]
        ]
    )

