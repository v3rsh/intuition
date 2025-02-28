# handlers/quiz.py

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from states import BotState
from database import get_user_by_id, update_user_progress, update_user_result, get_question
from keyboards import main_menu_kb, result_inline_keyboard, generate_quiz_answers
from utils import is_correct_answer, send_question, send_final_inline, send_welcome_message

router = Router()

@router.message(BotState.QUIZ)
async def quiz_handler(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user = await get_user_by_id(user_id)
    if not user:
        await message.answer("Ошибка: пользователь не найден. Нажмите /start")
        return
    
    # "в начало" → выходим в MAIN_MENU без изменения progress
    if message.text == "в начало":
        await state.set_state(BotState.MAIN_MENU)
        await send_welcome_message(message)
        return

    
    progress = user[3]  # уже отвеченные
    if progress >= 10:
        # Уже пройдено всё
        # пусть остаётся MAIN_MENU 
        await state.set_state(BotState.MAIN_MENU)
        await message.answer(
            "Вы уже прошли все вопросы!",
            reply_markup=ReplyKeyboardRemove()  # убираем клавиатуру
        )
        # Повторяем "финальное (второе) сообщение"
        await send_final_inline(message)
        return
    
    # Текущий вопрос = progress+1
    question_number = progress + 1
    question_data = await get_question(question_number)
    ...
    # если ответ один из 4...
    new_progress = progress + 1
    await update_user_progress(user_id, new_progress)

    if new_progress < 10:
        # Следующий вопрос:
        next_q = new_progress + 1
        await send_question(message, next_q)
    else:
        # new_progress=10 => все 10 вопросов отвечены
        # 1. "Спасибо за игру!" (убираем клавиатуру)
        
        # 2. Отправляем второе сообщение с инлайн-кнопкой
        await send_final_inline(message)
        # переводим пользователя в MAIN_MENU, чтоб осталась главная клавиатура
        await state.set_state(BotState.MAIN_MENU)