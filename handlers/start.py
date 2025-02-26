from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards import start_menu, after_test_menu
from states import StartState, TestState
from database import get_user_by_id, create_user

router = Router()

@router.message(commands=["start"])
async def cmd_start(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    username = message.from_user.username or "anonymous"
    
    # проверяем, есть ли пользователь в БД
    user = await get_user_by_id(user_id)
    if not user:
        # создаём, если нет
        await create_user(user_id, username)
        # переходим в состояние старт
        await state.set_state(StartState.waiting_for_action)
        await message.answer(
            "Привет! Добро пожаловать в нашу викторину «Интуиция».",
            reply_markup=start_menu()
        )
    else:
        # Если пользователь уже есть, смотрим его progress
        progress = user[3]  # progress = 0..11
        if progress == 0:
            # ещё не начинал
            await state.set_state(StartState.waiting_for_action)
            await message.answer(
                "С возвращением! Готов проверить свою интуицию?",
                reply_markup=start_menu()
            )
        elif 1 <= progress <= 10:
            # Прохождение теста не завершено
            await state.set_state(TestState.question_in_progress)
            await message.answer(
                "Вы не закончили викторину! Продолжим с текущего вопроса.",
                reply_markup=after_test_menu()  # или сразу отправить вопрос
            )
        else:
            # progress = 11 — значит тест уже пройден
            await message.answer(
                "Вы уже прошли викторину! Можно посмотреть результаты или выбрать обои.",
                reply_markup=after_test_menu()
            )
