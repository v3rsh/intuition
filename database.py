import aiosqlite
import csv
import os

DB_PATH = 'bot_database.db'
QUESTIONS_CSV = 'questions.csv'

async def init_db():
    """
    Создаёт таблицы Users и Questions (если не существуют)
    и загружает вопросы из CSV (если они ещё не загружены).
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Создаём таблицы
        await db.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                number INTEGER PRIMARY KEY AUTOINCREMENT,
                userid TEXT,
                username TEXT,
                progress INTEGER DEFAULT 0,  -- 0-11
                result INTEGER DEFAULT 0,    -- 0-10
                downloads INTEGER DEFAULT 0
            )
        ''')
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
        
        # Проверяем, есть ли уже данные в таблице Questions
        cursor = await db.execute('SELECT COUNT(*) FROM Questions')
        row = await cursor.fetchone()
        
        if row[0] == 0:  
            # Загружаем вопросы из CSV, если таблица пуста
            if os.path.exists(QUESTIONS_CSV):
                with open(QUESTIONS_CSV, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for r in reader:
                        await db.execute('''
                            INSERT INTO Questions (number, photo, correct, answer1, answer2, answer3)
                            VALUES (:number, :photo, :correct, :answer1, :answer2, :answer3)
                        ''', r)
        await db.commit()

async def get_user_by_id(user_id: str):
    """
    Получаем запись пользователя по user_id.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT * FROM Users WHERE userid = ?", (user_id,)
        )
        user = await cursor.fetchone()
    return user

async def create_user(user_id: str, username: str):
    """
    Создать нового пользователя, если его нет в БД.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO Users (userid, username)
            VALUES (?, ?)
        ''', (user_id, username))
        await db.commit()

async def update_user_progress(user_id: str, progress: int):
    """
    Обновить progress пользователя (0-11).
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            UPDATE Users
            SET progress = ?
            WHERE userid = ?
        ''', (progress, user_id))
        await db.commit()

async def update_user_result(user_id: str, new_result: int):
    """
    Обновить счётчик правильных ответов.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            UPDATE Users
            SET result = ?
            WHERE userid = ?
        ''', (new_result, user_id))
        await db.commit()

async def get_question(number: int):
    """
    Возвращает одну запись из таблицы Questions по номеру вопроса.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT number, photo, correct, answer1, answer2, answer3 FROM Questions WHERE number = ?",
            (number,)
        )
        return await cursor.fetchone()
