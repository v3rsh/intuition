from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states import BotState
from keyboards import main_menu_kb, wallpapers_menu, wallpapers_download_menu
from database import get_pic_by_button

router = Router()

@router.message(BotState.CHOOSE)
async def choose_wallpaper_handler(message: Message, state: FSMContext):
    if message.text == "в начало":
        await state.set_state(BotState.MAIN_MENU)
        await message.answer("Возврат в главное меню.", reply_markup=main_menu_kb())
        return
    
    # Предположим, что кнопки "обои1"..."обои4" - это поля button в таблице Pics
    # Если пользователь нажал одно из них, найдём соответствующую запись:
    pic_record = await get_pic_by_button(message.text)
    if pic_record:
        # pic_record = (id, button, pic, file)
        # Переходим в BotState.DOWNLOAD
        await state.set_state(BotState.DOWNLOAD)
        big_file_path = pic_record[3]
        
        # Отправляем big_file_path (допустим, это может быть URL или локальный путь)
        try:
            # Если это URL:
            if big_file_path.startswith("http"):
                await message.answer_document(
                    document=big_file_path,
                    caption="Вот файл в большом разрешении",
                    reply_markup=wallpapers_download_menu()
                )
            else:
                with open(big_file_path, 'rb') as f:
                    await message.answer_document(
                        document=f,
                        caption="Вот файл в большом разрешении",
                        reply_markup=wallpapers_download_menu()
                    )
        except FileNotFoundError:
            await message.answer(
                "Файл с обоями не найден, попробуйте другой вариант.",
                reply_markup=wallpapers_menu()
            )
    else:
        await message.answer(
            "Нужно выбрать один из четырёх вариантов или 'в начало'.",
            reply_markup=wallpapers_menu()
        )

@router.message(BotState.DOWNLOAD)
async def download_wallpaper_handler(message: Message, state: FSMContext):
    if message.text == "Выбрать другие обои":
        await state.set_state(BotState.CHOOSE)
        await message.answer(
            "Ок, выберите ещё обои:",
            reply_markup=wallpapers_menu()
        )
    elif message.text == "в начало":
        await state.set_state(BotState.MAIN_MENU)
        await message.answer("Возврат в главное меню.", reply_markup=main_menu_kb())
    else:
        await message.answer(
            "Нажмите 'Выбрать другие обои' или 'в начало'.",
            reply_markup=wallpapers_download_menu()
        )
