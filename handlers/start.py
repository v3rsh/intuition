from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards import start_menu, after_test_menu
from states import BotStates
from database import get_user_by_id, create_user

router = Router()

@router.message(F.text == "старт")
async def handle_start_text(message: Message, state: FSMContext):
    """
    При вводе текста "старт" проверяем пользователя в БД
    и переводим в нужное состояние.
    """
    user_id = str(message.from_user.id)
    username = message.from_user.username or "anonymous"
    
    # Проверяем/создаём пользователя
    user = await get_user_by_id(user_id)
    if not user:
        await create_user(user_id, username)
    
    # Повторно получаем данные (уже точно есть)
    user = await get_user_by_id(user_id)
    progress = user[3]  # progress = 0..11

    if progress == 0:
        # Ещё не начинал — главное меню
        await state.set_state(BotStates.MAIN_MENU)
        await message.answer(
            "Привет! Добро пожаловать в нашу викторину «Интуиция».",
            reply_markup=start_menu()
        )
    elif 1 <= progress <= 10:
        # Пользователь в середине викторины
        await state.set_state(BotStates.QUIZ)
        await message.answer(
            "Вы не закончили викторину! Продолжим с текущего вопроса.",
            reply_markup=after_test_menu()
        )
    else:
        # progress = 11 — викторина пройдена
        await message.answer(
            "Вы уже прошли викторину! Можно посмотреть результаты или выбрать обои.",
            reply_markup=after_test_menu()
        )
