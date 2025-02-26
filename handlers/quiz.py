from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states import BotState
from database import get_user_by_id, update_user_progress, update_user_result, get_question
from keyboards import main_menu_kb, result_inline_keyboard
from keyboards import generate_quiz_answers
from utils import is_correct_answer

router = Router()

@router.message(BotState.QUIZ)
async def quiz_handler(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user = await get_user_by_id(user_id)
    if not user:
        await message.answer("Ошибка: пользователь не найден. Нажмите /start")
        return
    
    progress = user[3]  # 1..10
    if message.text == "в начало":
        # Возвращаемся в MAIN_MENU, не меняя прогресс
        await state.set_state(BotState.MAIN_MENU)
        await message.answer("Возврат в главное меню", reply_markup=main_menu_kb())
        return
    
    # Ищем текущий вопрос (progress)
    question_data = await get_question(progress)
    if not question_data:
        await message.answer("Вопрос не найден в базе. Остановимся.")
        return
    
    correct = question_data[2]  # correct answer
    answers = [question_data[3], question_data[4], question_data[5], correct]

    # Проверяем, нажал ли пользователь на один из вариантов
    if message.text in answers:
        # Если ответ верный
        if is_correct_answer(message.text, correct):
            # result + 1
            current_result = user[4]
            await update_user_result(user_id, current_result+1)
        
        # progress + 1
        new_progress = progress + 1
        await update_user_progress(user_id, new_progress)
        
        if new_progress <= 9:
            # Задаём следующий вопрос
            await send_next_question(message, new_progress)
        else:
            # new_progress=10 => пользователь всё прошёл
            await state.set_state(BotState.RESULT)
            # Можно поздравить и показать inline-кнопки
            await message.answer(
                "Спасибо за игру!\n\n"
                "Интересно узнать результаты? Наберись терпения — "
                "ответы будут по ссылке ниже 5 марта! Не забудь проверить.\n"
                "И помни, самое главное — доверять себе❤️",
                reply_markup=result_inline_keyboard()
            )
    else:
        # Нажал что-то левое / или не совпадает ни с одним вариантом
        await message.answer(
            "Нужно выбрать один из вариантов ответа!",
            reply_markup=generate_quiz_answers(correct, answers=[question_data[3], question_data[4], question_data[5]])
        )

async def send_next_question(message: Message, question_number: int):
    """
    Отправляем вопрос №question_number. Аналогично тому, что делали в menu.py
    """
    question_data = await get_question(question_number)
    if not question_data:
        await message.answer("Ошибка: вопрос не найден.")
        return
    
    _, photo, correct, a1, a2, a3 = question_data
    kb = generate_quiz_answers(correct, [a1, a2, a3])
    try:
        with open(photo, 'rb') as ph:
            await message.answer_photo(
                photo=ph,
                caption=f"Вопрос №{question_number}. Твой ответ?",
                reply_markup=kb
            )
    except FileNotFoundError:
        await message.answer(
            text=f"Вопрос №{question_number} (файл не найден).",
            reply_markup=kb
        )
