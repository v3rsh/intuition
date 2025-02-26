from aiogram import Router, F
from aiogram.types import Message
from keyboards import results_inline_keyboard
from database import get_user_by_id

router = Router()

@router.message(F.text == "результаты")
async def show_results(message: Message):
    user_id = str(message.from_user.id)
    user = await get_user_by_id(user_id)
    if not user:
        await message.answer("Ошибка: пользователь не найден.")
        return
    
    result = user[4]  # индекс 4 = result
    await message.answer(
        f"Ваш результат: {result} правильных ответов из 10",
        reply_markup=results_inline_keyboard()
    )
