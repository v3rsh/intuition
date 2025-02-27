from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext

from states import BotState
from keyboards import main_menu_kb, dynamic_wallpapers_menu, wallpapers_download_menu
from database import get_pic_by_button, get_all_pics

router = Router()

@router.message(BotState.CHOOSE)
async def choose_wallpaper_handler(message: Message, state: FSMContext):
    if message.text == "в начало":
        await state.set_state(BotState.MAIN_MENU)
        await message.answer("Возврат в главное меню.", reply_markup=main_menu_kb())
        return
    
    # Ищем запись в Pics по нажатой кнопке (поле button)
    pic_record = await get_pic_by_button(message.text)
    if pic_record:
        # pic_record = (id, button, pic, file)
        await state.set_state(BotState.DOWNLOAD)
        big_file_path = pic_record[3]
        try:
            await message.answer_document(
                document=FSInputFile(big_file_path),
                caption="Вот файл в большом разрешении",
                reply_markup=wallpapers_download_menu()
            )
        except FileNotFoundError:
            # Если файл не найден, снова показываем клавиатуру с динамическими кнопками
            all_pics = await get_all_pics()
            all_buttons = [r[1] for r in all_pics]
            await message.answer(
                "Файл с обоями не найден, попробуйте другой вариант.",
                reply_markup=dynamic_wallpapers_menu(all_buttons)
            )
    else:
        # Если запись не найдена, формируем клавиатуру из всех доступных вариантов
        all_pics = await get_all_pics()
        all_buttons = [r[1] for r in all_pics]
        await message.answer(
            "Нужно выбрать один из вариантов или 'в начало'.",
            reply_markup=dynamic_wallpapers_menu(all_buttons)
        )



@router.message(BotState.DOWNLOAD)
async def download_wallpaper_handler(message: Message, state: FSMContext):
    from database import get_user_by_id, update_user_loads, get_all_pics
    from keyboards import main_menu_kb, wallpapers_download_menu, dynamic_wallpapers_menu

    user_id = str(message.from_user.id)
    user = await get_user_by_id(user_id)
    if not user:
        await message.answer("Ошибка: пользователь не найден. Нажмите /start")
        return

    # Индекс поля loads: (number=0, userid=1, username=2, progress=3, result=4, loads=5)
    current_loads = user[5]
    new_loads = current_loads + 1
    await update_user_loads(user_id, new_loads)

    if message.text == "Выбрать другие обои":
        await state.set_state(BotState.CHOOSE)
        # Получаем все записи обоев для формирования клавиатуры
        all_pics = await get_all_pics()
        all_buttons = [r[1] for r in all_pics]  # r[1] – значение поля button
        await message.answer(
            "Ок, выберите ещё обои:",
            reply_markup=dynamic_wallpapers_menu(all_buttons)
        )
    elif message.text == "в начало":
        await state.set_state(BotState.MAIN_MENU)
        await message.answer("Возврат в главное меню.", reply_markup=main_menu_kb())
    else:
        await message.answer(
            "Нажмите 'Выбрать другие обои' или 'в начало'.",
          
