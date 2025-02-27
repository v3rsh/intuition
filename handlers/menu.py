from aiogram import Router, F
from aiogram.types import Message, FSInputFile, InputMediaPhoto, InputMedia
from aiogram.fsm.context import FSMContext

from states import BotState
from database import get_user_by_id, update_user_progress, get_all_pics
from keyboards import main_menu_kb, dynamic_wallpapers_menu
from keyboards import generate_quiz_answers, result_inline_keyboard
from utils import is_correct_answer, send_question

router = Router()

@router.message(BotState.MAIN_MENU, F.text == "проверить интуицию")
async def main_menu_check_intuition(message: Message, state: FSMContext):
    """
    Пользователь нажал "проверить интуицию" в главном меню.
    Проверяем его progress, если < 10, переходим в QUIZ и показываем вопрос.
    Иначе (10) — показываем финальный экран.
    """
    user_id = str(message.from_user.id)
    user = await get_user_by_id(user_id)
    if not user:
        await message.answer("Ошибка: пользователя нет в базе. Нажмите /start")
        return
    
    progress = user[3]  # progress = 0..10
    if progress < 10:
        # Ставим состояние QUIZ
        await state.set_state(BotState.QUIZ)
        # Переходим к вопросу progress+1
        next_question = progress + 1
        await update_user_progress(user_id, next_question)
        await send_question(message, next_question)
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
    Пользователь выбрал 'сейчас не до игр'.
    Переход в состояние CHOOSE, отправляем миниатюры как медиа-группу
    + динамическую клавиатуру (названия и 'в начало').
    """
    await state.set_state(BotState.CHOOSE)

    rows = await get_all_pics()
    if not rows:
        await message.answer("Обои пока не добавлены в базу.")
        return

    media = []
    for i, (pic_id, button, pic_url, file_url) in enumerate(rows):
        caption = f"Обои: {button}"
        # Проверяем, локальный файл или http:
        if pic_url.startswith("http"):
            media.append(InputMediaPhoto(media=pic_url, caption=caption))
        else:
            media.append(InputMediaPhoto(media=FSInputFile(pic_url), caption=caption))

        if i == 9:
            break

    await message.answer_media_group(media=media)

    # Динамическая клавиатура
    all_buttons = [row[1] for row in rows]  # row[1] = button
    kb = dynamic_wallpapers_menu(all_buttons)
    await message.answer("Выберите обои из списка:", reply_markup=kb)

async def send_quiz_question(message: Message, question_number: int):
    """
    Отправляет вопрос (фото + 4 варианта + 'в начало').
    """
    from database import get_question
    from keyboards import generate_quiz_answers

    question_data = await get_question(question_number)
    if not question_data:
        await message.answer("Ошибка: вопрос не найден в базе.")
        return
    
    # question_data = (number, photo, correct, ans1, ans2, ans3, question) — если у вас 7 полей
    _, photo, correct, ans1, ans2, ans3, question= question_data[:6]  # если 6 полей
    # или распакуйте 7 полей, если есть question_text

    kb = generate_quiz_answers(correct, [ans1, ans2, ans3])
    try:
        with open(photo, 'rb') as ph:
            await message.answer_photo(
                photo=ph,
                caption=f"Вопрос №{question_number}. Твой ответ?",
                reply_markup=kb
            )
    except FileNotFoundError:
        await message.answer(
            text=f"Вопрос №{question_number} (файл не найден).",
            reply_markup=kb
        )
