import aiosqlite
import csv
import os

DB_PATH = 'data/bot.db'
QUESTIONS_CSV = 'data/questions.csv'
PICS_CSV = 'pics.csv'  # Допустим, для заполнения таблицы Pics

async def init_db():
    """
    Создаёт таблицы Users, Questions, Pics (если не существуют)
    и загружает данные из CSV, если таблицы пусты.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Таблица пользователей
        await db.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                number INTEGER PRIMARY KEY AUTOINCREMENT,
                userid TEXT,
                username TEXT,
                progress INTEGER DEFAULT 0,  -- 0..10
                result INTEGER DEFAULT 0,     -- 0..10
                loads INTEGER DEFAULT 0
            )
        ''')
        
        # Таблица вопросов
        await db.execute('''
            CREATE TABLE IF NOT EXISTS Questions (
                number INTEGER PRIMARY KEY,
                photo TEXT,
                correct TEXT,
                answer1 TEXT,
                answer2 TEXT,
                answer3 TEXT
            )
        ''')
        
        # Таблица обоев
        await db.execute('''
            CREATE TABLE IF NOT EXISTS Pics (
                id INTEGER,
                button TEXT,  -- например, 'обои1'
                pic TEXT,     -- путь к мелкой картинке (опционально)
                file TEXT     -- путь к большой картинке
            )
        ''')
        
        # Проверяем, есть ли уже данные в Questions
        cursor_q = await db.execute('SELECT COUNT(*) FROM Questions')
        row_q = await cursor_q.fetchone()
        if row_q[0] == 0 and os.path.exists(QUESTIONS_CSV):
            # Загружаем вопросы из CSV
            with open(QUESTIONS_CSV, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for r in reader:
                    await db.execute('''
                        INSERT INTO Questions (number, photo, correct, answer1, answer2, answer3)
                        VALUES (:number, :photo, :correct, :answer1, :answer2, :answer3)
                    ''', r)
        
        # Проверяем, есть ли данные в Pics
        cursor_p = await db.execute('SELECT COUNT(*) FROM Pics')
        row_p = await cursor_p.fetchone()
        if row_p[0] == 0 and os.path.exists(PICS_CSV):
            # Загружаем данные обоев
            with open(PICS_CSV, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for r in reader:
                    await db.execute('''
                        INSERT INTO Pics (button, pic, file)
                        VALUES (:button, :pic, :file)
                    ''', r)
        
        await db.commit()

async def get_user_by_id(user_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT * FROM Users WHERE userid = ?", (user_id,))
        return await cursor.fetchone()

async def create_user(user_id: str, username: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('INSERT INTO Users (userid, username) VALUES (?, ?)', (user_id, username))
        await db.commit()

async def update_user_progress(user_id: str, new_progress: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE Users SET progress = ? WHERE userid = ?', (new_progress, user_id))
        await db.commit()

async def update_user_result(user_id: str, new_result: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE Users SET result = ? WHERE userid = ?', (new_result, user_id))
        await db.commit()

async def get_question(number: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT number, photo, correct, answer1, answer2, answer3
            FROM Questions
            WHERE number = ?
        ''', (number,))
        return await cursor.fetchone()

async def get_pic_by_button(button_text: str):
    """
    Находим запись в Pics, у которой button = button_text.
    Возвращаем (id, button, pic, file) или None
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT * FROM Pics WHERE button = ?', (button_text,))
        return await cursor.fetchone()

async def get_all_pics():
    """
    Возвращает список кортежей (id, button, pic, file) из таблицы Pics.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT id, button, pic, file FROM Pics")
        return await cursor.fetchall()
    
    
async def update_user_loads(user_id: str, new_loads: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            UPDATE Users
            SET loads = ?
            WHERE userid = ?
        ''', (new_loads, user_id))
        await db.commit()
