# handlers/menu.py

from aiogram import Router, F
from aiogram.types import Message, FSInputFile, InputMediaPhoto, InputMedia
from aiogram.fsm.context import FSMContext

from states import BotState
from database import get_user_by_id, get_all_pics
from keyboards import main_menu_kb, dynamic_wallpapers_menu
from keyboards import result_inline_keyboard
from utils import send_question, send_final_inline

router = Router()

@router.message(BotState.MAIN_MENU, F.text == "проверить интуицию")
async def main_menu_check_intuition(message: Message, state: FSMContext):
    """
    Пользователь нажал "проверить интуицию" в главном меню.
    progress = число уже отвеченных вопросов.
    Если progress<10, показываем вопрос (progress+1).
    Если progress=10, всё завершено.
    """
    from database import get_user_by_id

    user_id = str(message.from_user.id)
    user = await get_user_by_id(user_id)
    if not user:
        await message.answer("Ошибка: пользователь не найден. Нажмите /start")
        return
    
    progress = user[3]  # 0..10
    if progress >= 10:
        # Всё пройдено
        await send_final_inline(message)
    else:
        # Меняем состояние на QUIZ
        await state.set_state(BotState.QUIZ)

        # Следующий вопрос = progress+1
        question_number = progress + 1
        await send_question(message, question_number)

@router.message(BotState.MAIN_MENU, F.text == "пока не до игр...")
async def main_menu_wallpapers(message: Message, state: FSMContext):
    """
    Переходим в состояние CHOOSE, отправляем миниатюры.
    """
    from database import get_all_pics

    await state.set_state(BotState.CHOOSE)
    rows = await get_all_pics()
    if not rows:
        await message.answer("Обои пока не добавлены в базу.")
        return

    media = []
    for i, (id, button, pic, file) in enumerate(rows):
        caption = None
        media.append(InputMediaPhoto(media=FSInputFile(pic), caption=caption))
        if i == 9:
            break


    all_buttons = [row[1] for row in rows]  # row[1]=button
    kb = dynamic_wallpapers_menu(all_buttons)
    await message.answer("Самое главное — хорошее настроение! /n"
                         "Лови 4 красивых заставки для телефона, пусть они поддерживают и вдохновляют тебя!")
    await message.answer_media_group(media=media)
    await message.answer("Выберите обои из списка:", reply_markup=kb)
