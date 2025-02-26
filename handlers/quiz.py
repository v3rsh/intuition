from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states import StartState, TestState
from database import (get_user_by_id, get_question, update_user_progress, 
                      update_user_result)
from keyboards import generate_answers_keyboard, after_test_menu, start_menu
from utils import is_correct_answer

router = Router()

@router.message(F.text == "проверить интуицию")
async def start_quiz(message: Message, state: FSMContext):
    """
    Если пользователь нажимает "проверить интуицию" с главного меню
    - нужно отправить первый/текущий вопрос, если ещё не пройден тест.
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
        
        # Устанавливаем состояние
        await state.set_state(TestState.question_in_progress)
        
        # Отправляем текущий вопрос
        await send_question(message, user_id, progress)
    else:
        # Если почему-то пользователя нет, создадим
        # (обычно этого не должно случиться, т.к. при /start создаём)
        await message.answer("Ошибка: пользователь не найден в БД.")
        return

@router.message(TestState.question_in_progress)
async def handle_quiz_answers(message: Message, state: FSMContext):
    """
    Обрабатываем 4 варианта ответа и кнопку 'в начало'.
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
        # Не сбрасываем прогресс, просто переводим state в StartState
        await state.set_state(StartState.waiting_for_action)
        await message.answer(
            "Ок, вернулись в начало.",
            reply_markup=start_menu()
        )
        return
    
    # Иначе — это один из вариантов ответа
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
        # Все 10 вопросов пройдены, устанавливаем progress = 11
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
    
    # question_data = (number, photo, correct, answer1, answer2, answer3)
    photo_path = question_data[1]
    correct_answer = question_data[2]
    ans1, ans2, ans3 = question_data[3], question_data[4], question_data[5]

    # Собираем и отправляем фото (можно поменять метод на send_document или send_photo)
    with open(photo_path, 'rb') as photo_file:
        await message.answer_photo(
            photo=photo_file,
            caption=f"Вопрос №{question_number}. Ваш вариант?",
            reply_markup=generate_answers_keyboard(correct_answer, [ans1, ans2, ans3])
        )
