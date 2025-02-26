import asyncio
import logging
import redis

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage

from config import BOT_TOKEN, REDIS_HOST, REDIS_PORT
from database import init_db
from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.quiz import router as quiz_router
from handlers.wallpapers import router as wallpapers_router
from handlers.callback import router as callback_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    storage = RedisStorage(redis=r)

    # Если хотите глобальный parse_mode, например MarkdownV2:
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="MarkdownV2")
    )
    
    dp = Dispatcher(storage=storage)

    # Подключаем роутеры
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(quiz_router)
    dp.include_router(wallpapers_router)
    dp.include_router(callback_router)

    # Инициализируем БД
    await init_db()

    logger.info("Starting bot polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
