from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states import BotStates
from keyboards import wallpapers_menu, wallpaper_download_menu, start_menu
from database import get_user_by_id

router = Router()

@router.message(BotStates.MAIN_MENU, F.text == "сейчас не до игр")
async def start_wallpapers(message: Message, state: FSMContext):
    """
    Пользователь из главного меню выбрал "сейчас не до игр" -> переходим на выбор обоев.
    """
    await state.set_state(BotStates.WALLPAPER_CHOOSE)
    await message.answer(
        "Выберите обои:",
        reply_markup=wallpapers_menu()
    )

@router.message(BotStates.WALLPAPER_CHOOSE)
async def choose_wallpaper(message: Message, state: FSMContext):
    """
    Выбор одного из 4 обоев или возвращение 'в начало'.
    """
    if message.text == "в начало":
        await state.set_state(BotStates.MAIN_MENU)
        await message.answer("Ок, вернулись на главный экран", reply_markup=start_menu())
        return

    if message.text in ["обои1", "обои2", "обои3", "обои4"]:
        # Отправляем файл с бОльшим разрешением
        await state.set_state(BotStates.WALLPAPER_DOWNLOAD)
        await message.answer_document(
            document="https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png",
            caption="Вот ваш файл обоев",
            reply_markup=wallpaper_download_menu()
        )
    else:
        await message.answer("Выберите один из предложенных вариантов или 'в начало'.")

@router.message(BotStates.WALLPAPER_DOWNLOAD)
async def download_more(message: Message, state: FSMContext):
    """
    Состояние скачивания/повтора обоев.
    """
    if message.text == "в начало":
        await state.set_state(BotStates.MAIN_MENU)
        await message.answer("Вернулись на главный экран", reply_markup=start_menu())
        return
    elif message.text == "скачать ещё":
        await state.set_state(BotStates.WALLPAPER_CHOOSE)
        await message.answer("Выберите ещё обои:", reply_markup=wallpapers_menu())
    else:
        await message.answer("Нажмите 'скачать ещё' или 'в начало'.")
