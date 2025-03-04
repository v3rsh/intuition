# utils.py

from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from keyboards import generate_quiz_answers
from database import get_question
from config import logger

async def send_welcome_message(message: Message):
    """
    Отправляет приветственное сообщение (как при /start).
    """
    from keyboards import main_menu_kb
    await message.answer(
        "Привет! Хочешь проверить свою интуицию? Самое время! Впереди 10 вопросов о наших коллегах, и поверь, 10 самых неожиданных ответов! Желаем удачи🍀  \n\n"
        "P.S. Самых проницательных ждут приятные подарки!",
        reply_markup=main_menu_kb()
    )

async def send_question(message: Message, question_number: int):
    """
    Отправляем фото вопроса № question_number.
    - caption формируем из поля question (если есть), 
      либо "Вопрос №N" по умолчанию.
    - reply_markup = generate_quiz_answers(...)
    """
    question_data = await get_question(question_number)
    if not question_data:
        await message.answer(f"Ошибка: вопрос №{question_number} не найден.")
        return
    
    # question_data = (num, photo, correct, a1, a2, a3, q_text)
    num, photo, correct, a1, a2, a3, q_text = question_data
    if not q_text:
        q_text = f"Вопрос №{num}"  # fallback
    
    kb = generate_quiz_answers(correct, [a1, a2, a3])
    photo_path = question_data[1]
    logger.info(f"путь к фото: {photo_path}")
    try:
        await message.answer_photo(
            photo=FSInputFile(photo_path),
            caption=q_text,
            reply_markup=kb
        )
    except FileNotFoundError:
        await message.answer(
            text=f"{q_text}\n\n(Файл '{photo}' не найден).",
            reply_markup=kb
        )


def is_correct_answer(user_text: str, correct_text: str) -> bool:
    return user_text.strip().lower() == correct_text.strip().lower()


async def send_final_inline(message: Message, two_buttons: bool = True):
    """
    Отправляет первое финальное сообщение с удалением клавиатуры.
    """
    await message.answer(
            "Спасибо за игру!",
            reply_markup=ReplyKeyboardRemove()
        )
    """
    Отправляем финальное inline-сообщение.
    Если two_buttons=True, то [Ссылка, "в начало"].
    Иначе только [Ссылка].
    """
    link_text="Space"
    link="https://space.beeline.ru/News/Pages/2025/news_f05f751162024409807122436ccf811a.aspx"
    if two_buttons:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text=link_text, url=link),
                InlineKeyboardButton(text="в начало", callback_data="to_main")
            ]]
        )
    else:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text=link_text, url=link)
            ]]
        )

    # Текст берём из предыдущей версии или свой
    text = (
        "Интересно узнать результаты? Наберись терпения — "
        "ответы будут по ссылке ниже 5 марта! Не забудь проверить.\n"
        "И помни, самое главное — доверять себе❤️"
    )

    await message.answer(text, reply_markup=kb)