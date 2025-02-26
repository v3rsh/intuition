from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states import StartState, WallpaperState
from keyboards import wallpapers_menu, wallpaper_download_menu, start_menu
from database import get_user_by_id

router = Router()

@router.message(F.text == "сейчас не до игр")
async def start_wallpapers(message: Message, state: FSMContext):
    await state.set_state(WallpaperState.choosing_wallpapers)
    await message.answer(
        "Выберите обои:",
        reply_markup=wallpapers_menu()
    )

@router.message(WallpaperState.choosing_wallpapers)
async def choose_wallpaper(message: Message, state: FSMContext):
    if message.text == "в начало":
        await state.set_state(StartState.waiting_for_action)
        await message.answer("Ок, вернулись на главный экран", reply_markup=start_menu())
        return

    # Если пользователь выбрал из [обои1, обои2, обои3, обои4]
    if message.text in ["обои1", "обои2", "обои3", "обои4"]:
        # Отправляем файл с бОльшим разрешением
        # (в реальном случае пришлём разные картинки; для примера — одна заглушка)
        await state.set_state(WallpaperState.download_wallpapers)
        await message.answer_document(
            document="https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png",
            caption="Вот ваш файл обоев",
            reply_markup=wallpaper_download_menu()
        )
    else:
        await message.answer("Выберите один из предложенных вариантов или 'в начало'.")

@router.message(WallpaperState.download_wallpapers)
async def download_more(message: Message, state: FSMContext):
    # Пользователь либо жмёт 'скачать ещё', либо 'в начало'
    if message.text == "в начало":
        await state.set_state(StartState.waiting_for_action)
        await message.answer("Вернулись на главный экран", reply_markup=start_menu())
        return
    elif message.text == "скачать ещё":
        await state.set_state(WallpaperState.choosing_wallpapers)
        await message.answer("Выберите ещё обои:", reply_markup=wallpapers_menu())
    else:
        await message.answer("Нажмите 'скачать ещё' или 'в начало'.")
