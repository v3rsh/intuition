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
    "Привет! \n"
    "Поздравляем, твоя интуиция тебя не подвела и принесла тебе победу: 7 хобби отгаданы верно, это максимальный результат! \n\n"
    "Мы хотим наградить тебя приятным подарком, в котором будет наш стильный корпоративный мерч. Для оформления доставки ждём от тебя письмо, которое нужно направить со свой рабочей почты по адресу olalzotova@beeline.ru с указанием: \n\n"
    "- адреса офиса для курьерской доставки и контактного телефона \n"
    "- размера одежды \n"
    "- твоего ника в телеграм"
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
