from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from states import BotState
from keyboards import main_menu_kb

router = Router()

@router.callback_query(lambda call: call.data == "to_main")
async def callback_to_main(query: CallbackQuery, state: FSMContext):
    await state.set_state(BotState.MAIN_MENU)
    await query.message.answer(
        "Вы перешли в главное меню",
        reply_markup=main_menu_kb()
    )
    # Также не забываем answerCallbackQuery
    await query.answer()
