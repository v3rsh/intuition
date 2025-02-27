# utils.py
from aiogram.types import Message, FSInputFile
from keyboards import generate_quiz_answers
from database import get_question

async def send_question(message: Message, question_number: int):
    """
    Показываем вопрос № question_number:
    - Берём запись из БД (photo, correct, answer1..3)
    - Отправляем photo (через FSInputFile) + клавиатуру.
    """
    question_data = await get_question(question_number)
    if not question_data:
        await message.answer(f"Ошибка: вопрос №{question_number} не найден.")
        return
    
    # question_data = (num, photo, correct, a1, a2, a3, question_text?)...
    # Для примера распакуем первые 6:
    _, photo, correct, a1, a2, a3, *rest = question_data

    kb = generate_quiz_answers(correct, [a1, a2, a3])
    caption_text = f"Вопрос №{question_number}. Твой ответ?"

    try:
        await message.answer_photo(
            photo=FSInputFile(photo),
            caption=caption_text,
            reply_markup=kb
        )
    except FileNotFoundError:
        await message.answer(
            text=f"{caption_text}\n\n(Файл '{photo}' не найден).",
            reply_markup=kb
        )

def is_correct_answer(user_text: str, correct_text: str) -> bool:
    return user_text.strip().lower() == correct_text.strip().lower()
