import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
# Предположим, переменная WINNERS содержит строку с user_id, разделёнными запятыми:
WINNERS = os.getenv("WINNERS", "")

# Разбиваем строку по запятым и убираем лишние пробелы
winners_list = [uid.strip() for uid in WINNERS.split(",") if uid.strip()]

CONGRAT_MSG = (
    "Поздравляем! 🎉\n\n"
    "Вы стали победителем викторины «Интуиция».\n"
    "Спасибо за участие и оставайтесь на связи! напишите @priori89 для получения приза"
)

async def main():
    bot = Bot(token=BOT_TOKEN)
    for user_id in winners_list:
        try:
            await bot.send_message(user_id, CONGRAT_MSG)
            print(f"Сообщение отправлено пользователю {user_id}")
        except Exception as e:
            print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
