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
    [проверить интуицию] [сейчас не до игр]
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="проверить интуицию")],
            [KeyboardButton(text="сейчас не до игр")]
        ],
        resize_keyboard=True
    )

def wallpapers_menu():
    """
    Для BotState.CHOOSE: 4 варианта + в начало
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("обои1"), KeyboardButton("обои2")],
            [KeyboardButton("обои3"), KeyboardButton("обои4")],
            [KeyboardButton("в начало")]
        ],
        resize_keyboard=True
    )

def wallpapers_download_menu():
    """
    Для BotState.DOWNLOAD: [Выбрать другие обои][в начало]
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("Выбрать другие обои"), KeyboardButton("в начало")]
        ],
        resize_keyboard=True
    )

def generate_quiz_answers(correct_answer: str, answers: list):
    """
    4 варианта (correct + 3 answers), перемешанные.
    5-я кнопка: в начало.
    """
    variants = answers + [correct_answer]
    random.shuffle(variants)

    keyboard_layout = []
    row = []
    for i, ans in enumerate(variants, start=1):
        row.append(KeyboardButton(text=ans))
        if i % 2 == 0:
            keyboard_layout.append(row)
            row = []
    if row:
        keyboard_layout.append(row)

    # Кнопка 'в начало' в отдельной строке
    keyboard_layout.append([KeyboardButton("в начало")])

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
