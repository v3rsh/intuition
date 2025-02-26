from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states import BotStates
from database import (get_user_by_id, get_question, update_user_progress, 
                      update_user_result)
from keyboards import generate_answers_keyboard, after_test_menu, start_menu
from utils import is_correct_answer

router = Router()

@router.message(BotStates.MAIN_MENU, F.text == "проверить интуицию")
async def start_quiz(message: Message, state: FSMContext):
    """
    Пользователь нажал "проверить интуицию" в главном меню.
    Проверяем, где он остановился в викторине, отправляем нужный вопрос.
    """
    user_id = str(message.from_user.id)
    user = await get_user_by_id(user_id)
    
    if user:
        progress = user[3]  # текущий progress
        if progress == 11:
            # У пользователя тест уже пройден
            await message.answer(
                "Вы уже прошли викторину!",
                reply_markup=after_test_menu()
            )
            return
        
        # Если progress == 0, начинаем с 1-го вопроса
        if progress == 0:
            progress = 1
            await update_user_progress(user_id, progress)
        
        # Переводим пользователя в состояние QUIZ
        await state.set_state(BotStates.QUIZ)
        
        # Отправляем текущий вопрос
        await send_question(message, user_id, progress)
    else:
        # Если почему-то пользователя нет, сообщаем ошибку
        await message.answer("Ошибка: пользователь не найден в БД.")
        return

@router.message(BotStates.QUIZ)
async def handle_quiz_answers(message: Message, state: FSMContext):
    """
    Обрабатываем 4 варианта ответа и кнопку 'в начало'
    при состоянии QUIZ.
    """
    user_id = str(message.from_user.id)
    user = await get_user_by_id(user_id)
    
    if not user:
        await message.answer("Ошибка: пользователя нет в БД")
        return
    
    progress = user[3]  # 1..10
    if progress > 10:
        # Викторина уже пройдена
        await message.answer("Вы уже закончили викторину.", reply_markup=after_test_menu())
        return
    
    # Если пользователь жмёт 'в начало'
    if message.text == "в начало":
        # Не сбрасываем прогресс, просто переводим state -> MAIN_MENU
        await state.set_state(BotStates.MAIN_MENU)
        await message.answer(
            "Ок, вернулись в начало.",
            reply_markup=start_menu()
        )
        return
    
    # Иначе — пользователь выбрал один из 4 вариантов ответа
    question_data = await get_question(progress)
    correct_answer = question_data[2]  # индекс 2 = correct
    
    if is_correct_answer(message.text, correct_answer):
        # Ответ правильный
        current_result = user[4]  # result
        await update_user_result(user_id, current_result + 1)
    
    # Переходим к следующему вопросу
    next_progress = progress + 1
    await update_user_progress(user_id, next_progress)
    
    if next_progress <= 10:
        # Отправить следующий вопрос
        await send_question(message, user_id, next_progress)
    else:
        # Все 10 вопросов пройдены, ставим progress=11
        await update_user_progress(user_id, 11)
        await message.answer(
            "Поздравляем, вы прошли викторину!",
            reply_markup=after_test_menu()
        )

async def send_question(message: Message, user_id: str, question_number: int):
    """
    Отправляем пользователю фото + вопрос, формируем клавиатуру из 4 вариантов.
    """
    question_data = await get_question(question_number)
    if not question_data:
        await message.answer("Ошибка: нет данных по вопросу.")
        return
    
    photo_path = question_data[1]
    correct_answer = question_data[2]
    ans1, ans2, ans3 = question_data[3], question_data[4], question_data[5]

    with open(photo_path, 'rb') as photo_file:
        await message.answer_photo(
            photo=photo_file,
            caption=f"Вопрос №{question_number}. Ваш вариант?",
            reply_markup=generate_answers_keyboard(correct_answer, [ans1, ans2, ans3])
        )
