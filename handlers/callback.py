from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from utils import send_welcome_message
from states import BotState
from keyboards import main_menu_kb

router = Router()

@router.callback_query(lambda call: call.data == "to_main")
async def callback_to_main(query: CallbackQuery, state: FSMContext):
    await state.set_state(BotState.MAIN_MENU)
    await send_welcome_message(query.message)
    # Также не забываем answerCallbackQuery
    await query.answer()
