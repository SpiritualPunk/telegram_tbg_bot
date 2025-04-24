import os
import sqlite3
import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters, idle
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ✅ Переменные окружения от Railway
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

print("🚀 Бот запускается...")

# 🧠 Путь к базе (относительно этого файла)
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

# 🤖 Бот и планировщик
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
scheduler = AsyncIOScheduler()

# 📁 Работа с базой
def init_db():
    print("📦 Инициализация базы данных...")
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
    print("✅ База данных готова.")

def save_user(user):
    print(f"💾 Сохраняем пользователя: {user.id}")
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

# ⏰ Задача: сообщение через 1 минуту
async def send_course_step(user_id):
    print(f"📨 Отправляем сообщение пользователю {user_id}")
    try:
        await app.send_message(
            user_id,
            "✅ Это тестовое сообщение от Railway бота. Всё работает! 🥳"
        )
    except Exception as e:
        print(f"❌ Ошибка при отправке пользователю {user_id}: {e}")

def schedule_message(user_id):
    run_time = datetime.now() + timedelta(minutes=1)
    print(f"🕒 Планируем сообщение для {user_id} на {run_time}")
    scheduler.add_job(
        send_course_step,
        "date",
        run_date=run_time,
        args=[user_id],
        id=f"course_step_{user_id}",
        replace_existing=True
    )

# 📬 Команда /start
@app.on_message(filters.command("start"))
async def start_handler(client, message):
    user = message.from_user
    print(f"📥 Получен /start от {user.id}")
    save_user(user)
    await message.reply(
        f"Привет, {user.first_name}! 👋\n\nТы на тестовой версии. Сообщение придёт через минуту ⏱"
    )
    schedule_message(user.id)

# 🧠 Асинхронный запуск
async def main():
    init_db()
    scheduler.start()
    print("✅ Планировщик запущен")
    await app.start()
    print("🤖 Бот запущен и ждёт сообщений")
    await idle()
    await app.stop()

# ▶️ Старт
if __name__ == "__main__":
    asyncio.run(main())
