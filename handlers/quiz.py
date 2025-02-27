# handlers/quiz.py

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states import BotState
from database import get_user_by_id, update_user_progress, update_user_result, get_question
from keyboards import main_menu_kb, result_inline_keyboard, generate_quiz_answers
from utils import is_correct_answer, send_question

router = Router()

@router.message(BotState.QUIZ)
async def quiz_handler(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user = await get_user_by_id(user_id)
    if not user:
        await message.answer("Ошибка: пользователь не найден. Нажмите /start")
        return
    
    progress = user[3]  # число уже отвеченных вопросов (0..10)
    
    # "в начало" → выходим в MAIN_MENU без изменения progress
    if message.text == "в начало":
        await state.set_state(BotState.MAIN_MENU)
        await message.answer("Возврат в главное меню", reply_markup=main_menu_kb())
        return
    
    # Если progress >= 10, значит все вопросы отвечены
    if progress >= 10:
        await state.set_state(BotState.RESULT)
        await message.answer("Все вопросы уже отвечены!")
        return

    # Определяем: текущий вопрос -> progress+1
    question_number = progress + 1
    question_data = await get_question(question_number)
    if not question_data:
        await message.answer("Вопрос не найден в базе.")
        return
    
    correct = question_data[2]
    answers_list = [question_data[3], question_data[4], question_data[5], correct]

    # Если пользователь выбрал один из 4 вариантов
    if message.text in answers_list:
        # Проверяем правильность
        if is_correct_answer(message.text, correct):
            current_result = user[4]
            await update_user_result(user_id, current_result + 1)
        
        # progress += 1 (ответили ещё на один вопрос)
        new_progress = progress + 1
        await update_user_progress(user_id, new_progress)

        if new_progress < 10:
            # Показываем следующий вопрос = new_progress + 1
            next_q = new_progress + 1
            await send_question(message, next_q)
        else:
            # new_progress=10 => все вопросы отвечены
            await state.set_state(BotState.RESULT)
            await message.answer(
                "Спасибо за игру!\n\n"
                "Интересно узнать результаты? Наберись терпения — "
                "ответы будут по ссылке ниже 5 марта! Не забудь проверить.\n"
                "И помни, самое главное — доверять себе❤️",
                reply_markup=result_inline_keyboard()
            )
    else:
        # Если не один из 4 вариантов
        await message.answer(
            "Нужно выбрать один из вариантов ответа!",
            reply_markup=generate_quiz_answers(correct, [
                question_data[3],
                question_data[4],
                question_data[5]
            ])
        )
