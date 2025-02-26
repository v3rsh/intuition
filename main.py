import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
import redis

from config import BOT_TOKEN, REDIS_HOST, REDIS_PORT
from database import init_db
from handlers.start import router as start_router
from handlers.quiz import router as quiz_router
from handlers.wallpapers import router as wallpaper_router
from handlers.results import router as results_router

# Настраиваем логирование (пример)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Инициализируем redis-хранилище для FSM
    r = redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), decode_responses=True)
    storage = RedisStorage(redis=r)

    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=storage)

    # Подключаем роутеры
    dp.include_router(start_router)
    dp.include_router(quiz_router)
    dp.include_router(wallpaper_router)
    dp.include_router(results_router)

    # Инициализируем БД (создать таблицы, залить вопросы)
    await init_db()

    # Запускаем бота
    logger.info("Starting bot polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
