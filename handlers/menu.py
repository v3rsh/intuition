from aiogram import Router, F
from aiogram.types import Message, FSInputFile, InputMediaPhoto, InputMedia
from aiogram.fsm.context import FSMContext

from states import BotState
from database import get_user_by_id, update_user_progress, get_all_pics
from keyboards import main_menu_kb, dynamic_wallpapers_menu
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
    Пользователь выбрал 'сейчас не до игр'.
    1) Ставим состояние CHOOSE
    2) Отправляем все миниатюры (Pics.pic)
    3) Показываем клавиатуру (кнопки = Pics.button + 'в начало')
    """
    await state.set_state(BotState.CHOOSE)

    # 1) Получаем список обоев
    rows = await get_all_pics()  
    # rows – список [(id, button, pic, file), ...]

    # 2) Отправляем миниатюры. Можно:
    #    A) медиа-группой (до 10 штук в группе),
    #    B) по одному сообщению на картинку,
    #    C) или вообще без отправки картинок — решайте сами.

    # --- Вариант A: отправляем 1 медиа-группу (до 10 штук) ---
    # (Если обоев больше 10, придётся делать несколько групп)

    if not rows:
        await message.answer("Обои пока не добавлены в базу.")
        return

    media = []
    for i, (pic_id, button, pic_url, file_url) in enumerate(rows):
        # Собираем InputMediaPhoto
        # caption можно прописать для каждого, например:
        caption = f"Обои: {button}"
        # Если pic_url это http-URL:
        if pic_url.startswith("http"):
            media.append(InputMediaPhoto(media=pic_url, caption=caption))
        else:
            # Локальный файл
            media.append(InputMediaPhoto(media=FSInputFile(pic_url), caption=caption))
        
        # Если количество превысит 10, придётся рвать на части
        if i == 9:
            break

    await message.answer_media_group(media=media)

    # Если у вас >10 картинок, логика: отправить их в нескольких группах:
    # (Можно сделать "порции" по 10)

    # 3) Динамическая клавиатура (кнопки = button)
    all_buttons = [row[1] for row in rows]  # row[1] = button
    kb = dynamic_wallpapers_menu(all_buttons)
    await message.answer(
        "Выберите обои из списка:",
        reply_markup=kb
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
