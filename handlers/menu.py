from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states import BotState
from database import get_user_by_id, update_user_progress
from keyboards import main_menu_kb, wallpapers_menu
from keyboards import generate_quiz_answers
from keyboards import result_inline_keyboard
from utils import is_correct_answer

router = Router()

@router.message(BotState.MAIN_MENU, F.text == "проверить интуицию")
async def main_menu_check_intuition(message: Message, state: FSMContext):
    """
    Пользователь в главном меню нажал "проверить интуицию".
    Проверяем его progress.
    """
    user_id = str(message.from_user.id)
    user = await get_user_by_id(user_id)
    if not user:
        await message.answer("Ошибка: пользователя нет в базе. Нажмите /start")
        return
    
    progress = user[3]  # progress 0..10
    if progress < 10:
        # Устанавливаем state=QUIZ
        await state.set_state(BotState.QUIZ)
        # Отправим следующий вопрос (progress+1)
        next_question = progress + 1
        await update_user_progress(user_id, next_question)  # фиксируем в БД
        await send_quiz_question(message, next_question)
    else:
        # progress=10 => викторина закончена
        await state.set_state(BotState.RESULT)
        await message.answer(
            "У вас уже пройдена вся викторина (10 вопросов)! Вот ваш результат:",
            reply_markup=result_inline_keyboard()
        )

@router.message(BotState.MAIN_MENU, F.text == "сейчас не до игр")
async def main_menu_wallpapers(message: Message, state: FSMContext):
    """
    Пользователь выбрал 'сейчас не до игр',
    переходим в состояние CHOOSE обоев.
    """
    await state.set_state(BotState.CHOOSE)
    await message.answer(
        "Выберите обои из списка:",
        reply_markup=wallpapers_menu()
    )

async def send_quiz_question(message: Message, question_number: int):
    """
    Отправляет вопрос (фото + 4 варианта + кнопка в начало).
    Реализована отдельно, чтобы вызывать и в quiz-хендлере.
    """
    from database import get_question  # локальный импорт, чтобы избежать циклов
    from keyboards import generate_quiz_answers

    question_data = await get_question(question_number)
    if not question_data:
        await message.answer("Ошибка: вопрос не найден в базе.")
        return
    
    _, photo, correct, ans1, ans2, ans3 = question_data
    try:
        with open(photo, 'rb') as ph:
            await message.answer_photo(
                photo=ph,
                caption=f"Вопрос №{question_number}. Твой ответ?",
                reply_markup=generate_quiz_answers(correct, [ans1, ans2, ans3])
            )
    except FileNotFoundError:
        # Если файла нет, просто отправим текст
        await message.answer(
            text=f"Вопрос №{question_number}. Файл не найден, но вот варианты",
            reply_markup=generate_quiz_answers(correct, [ans1, ans2, ans3])
        )
