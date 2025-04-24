

import os
import sqlite3
import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters, idle
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# 🔐 ВСТАВЬ СВОИ ДАННЫЕ
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 🗂️ Путь к базе данных (абсолютный путь — важно для PythonAnywhere)
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

# 🤖 Инициализация клиента и планировщика
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
scheduler = AsyncIOScheduler()

# 📁 Работа с базой данных
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            username TEXT,
            registered_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_user(user):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, first_name, username, registered_at) VALUES (?, ?, ?, ?)", (
        user.id,
        user.first_name,
        user.username,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

# ⏰ Планировка сообщения
async def send_course_step(user_id):
    try:
        await app.send_message(
            user_id,
            "Доброе утро! ☀️ Первый шаг очищающего курса:\n\n🍋 Выпей стакан тёплой воды с лимоном."
        )
    except Exception as e:
        print(f"Ошибка отправки пользователю {user_id}: {e}")

def schedule_message(user_id):
    test_time = datetime.now() + timedelta(minutes=1)  # через 2 минуту

    scheduler.add_job(
        send_course_step,
        "date",
        run_date=test_time,
        args=[user_id],
        id=f"test_course_step_{user_id}",
        replace_existing=True
    )

# 📬 Обработка /start
@app.on_message(filters.command("start"))
async def start_handler(client, message):
    user = message.from_user
    save_user(user)
    await message.reply(
        f"Привет, {user.first_name}! 👋\n\nДобро пожаловать в мини-курс по очищению. Мы начнём завтра утром 🌞"
    )
    schedule_message(user.id)

# 🧠 Асинхронный main
async def main():
    init_db()
    scheduler.start()
    print("✅ Планировщик запущен")
    await app.start()
    await idle()
    await app.stop()

# ▶️ Запуск
if __name__ == "__main__":
    asyncio.run(main())

