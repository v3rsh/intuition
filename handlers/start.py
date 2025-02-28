from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states import BotState
from database import get_user_by_id, create_user
from keyboards import main_menu_kb
from utils import send_welcome_message

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    username = message.from_user.username or "anonymous"

    # Создаём пользователя, если нет
    user = await get_user_by_id(user_id)
    if not user:
        await create_user(user_id, username)

    # Ставим состояние MAIN_MENU
    await state.set_state(BotState.MAIN_MENU)
    await send_welcome_message()
