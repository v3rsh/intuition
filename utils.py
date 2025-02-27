# utils.py 

import random
import os
from aiogram.types import Message
from keyboards import generate_quiz_answers
from database import get_question



async def send_question(message: Message, question_number: int):
    """
    Универсальная функция для отправки вопроса:
    - Получает запись вопроса (фото, ответы) из БД.
    - Отправляет фото (или текст, если файла нет) + клавиатуру из 4 вариантов и 'в начало'.
    """
    question_data = await get_question(question_number)
    if not question_data:
        await message.answer(f"Ошибка: вопрос №{question_number} не найден.")
        return
    
    # Предположим, что в таблице 6 или 7 полей, в зависимости от наличия `question`
    # Например, (num, photo, correct, ans1, ans2, ans3)
    # или (num, photo, correct, ans1, ans2, ans3, question_text)
    # Ниже пример на 6 полях:
    _, photo, correct, a1, a2, a3 = question_data[:6]

    # Генерируем клавиатуру (4 ответа + 'в начало')
    answers_kb = generate_quiz_answers(correct, [a1, a2, a3])

    caption_text = f"Вопрос №{question_number}. Твой ответ?"

    # Пытаемся открыть файл
    try:
        with open(photo, 'rb') as ph:
            await message.answer_photo(
                photo=ph,
                caption=caption_text,
                reply_markup=answers_kb
            )
    except FileNotFoundError:
        await message.answer(
            text=f"{caption_text}\n\n(файл не найден).",
            reply_markup=answers_kb
        )


def is_correct_answer(user_text: str, correct_text: str) -> bool:
    """
    Сравнение ответов без учёта регистра и ведущих/замыкающих пробелов
    """
    return user_text.strip().lower() == correct_text.strip().lower()
