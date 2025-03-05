import asyncio
import aiosqlite
import csv
import os

DB_PATH = 'data/bot.db'       # путь к вашей БД
EXPORT_CSV = 'data/Users.csv' # куда сохранять результаты

async def export_users_to_csv():
    # Проверим, что папка data/ существует
    os.makedirs(os.path.dirname(EXPORT_CSV), exist_ok=True)

    # Подключаемся к БД
    async with aiosqlite.connect(DB_PATH) as db:
        # Делаем запрос
        cursor = await db.execute("""
            SELECT number, userid, username, progress, result, loads
            FROM Users
        """)
        rows = await cursor.fetchall()
        await cursor.close()

    # Сохраняем в CSV
    with open(EXPORT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        # заголовки
        writer.writerow(["number", "userid", "username", "progress", "result", "loads"])
        # записываем все строки
        for row in rows:
            writer.writerow(row)

def main():
    asyncio.run(export_users_to_csv())

if __name__ == '__main__':
    main()
