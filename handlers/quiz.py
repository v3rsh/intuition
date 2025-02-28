# handlers/quiz.py

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from states import BotState
from database import (
    get_user_by_id,
    get_question,
    update_user_progress,
    update_user_result
)
from keyboards import main_menu_kb, generate_quiz_answers
from utils import (
    is_correct_answer,
    send_question,
    send_welcome_message,
    send_final_inline
)

router = Router()

@router.message(BotState.QUIZ)
async def quiz_handler(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user = await get_user_by_id(user_id)
    if not user:
        await message.answer("Ошибка: пользователь не найден. Нажмите /start")
        return
    
    # "в начало": уходим в MAIN_MENU (приветственное сообщение),
    # progress НЕ меняем
    if message.text == "в начало":
        await state.set_state(BotState.MAIN_MENU)
        await send_welcome_message(message)
        return

    progress = user[3]  # уже отвеченные вопросы (0..10)

    # Текущий вопрос = progress+1
    question_number = progress + 1
    question_data = await get_question(question_number)
    if not question_data:
        await message.answer("Вопрос не найден в базе.")
        return

    # question_data = (num, photo, correct, a1, a2, a3, question_text)
    correct = question_data[2]
    answers_list = [question_data[3], question_data[4], question_data[5], correct]

    # Если пользователь ввёл один из 4 вариантов
    if message.text in answers_list:
        # Проверяем, верно ли
        if is_correct_answer(message.text, correct):
            current_result = user[4]  # user[4] = result
            await update_user_result(user_id, current_result + 1)
        
        # Увеличиваем progress (ответили ещё на 1 вопрос)
        new_progress = progress + 1
        await update_user_progress(user_id, new_progress)

        if new_progress < 10:
            # Показываем следующий вопрос:
            next_q = new_progress + 1
            await send_question(message, next_q)
        else:
            # new_progress=10 => последний ответ
            await send_final_inline(message, two_buttons=True)

    else:
        # Неправильный ввод (не один из 4 вариантов и не "в начало")
        await message.answer("Нужно выбрать один из вариантов ответа!")
