from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
 ApplicationBuilder,
 CommandHandler,
 MessageHandler,
 filters,
 ContextTypes,
)
import os
from psycopg2 import connect
import psycopg2

TOKEN = "8931077914:AAH3sS6UTqy7uCb61YIms80hvnnuGOZknNo"
ADMIN_ID = 7938699279

DATABASE_URL = os.getenv('DATABASE_URL')

# Функция для получения соединения
def get_connection():
    try:
        return connect(DATABASE_URL)
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return None

# Инициализация БД
def init_db():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
             user_id BIGINT PRIMARY KEY,
             name TEXT,
             group_name TEXT
            )
            """)
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ БД инициализирована")
        except Exception as e:
            print(f"❌ Ошибка инициализации БД: {e}")

schedule = {
 "ИС-21": """
📚 Расписание группы ИС-21
📘 Понедельник
• Математика
• Информатика
📗 Вторник
• Английский
• Физика
""",
 "П-14": """
📚 Расписание группы П-14
📘 Понедельник
• История
• Биология
📗 Вторник
• Химия
• География
"""
}

keyboard = ReplyKeyboardMarkup(
 [
 ["📅 Расписание", "⏰ Ближайшая пара"],
 ["📝 Домашка", "🏆 Оценки"],
 ["👨‍🏫 Консультация", "📅 Экзамены"],
 ["📚 Материалы", "📢 Новости"],
 ["💰 Стипендия", "🏫 Кабинеты"],
 ["👤 Мой профиль", "📞 Контакты"],
 ["❓ Помощь"]
 ],
 resize_keyboard=True
)

waiting_for_registration = set()
waiting_for_consultation = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
 user_id = update.message.from_user.id
 conn = get_connection()
 if not conn:
 await update.message.reply_text("❌ Ошибка подключения к БД")
 return
 
 try:
 cursor = conn.cursor()
 cursor.execute(
 "SELECT * FROM users WHERE user_id=%s",
 (user_id,)
 )
 user = cursor.fetchone()
 cursor.close()
 
 if not user:
 waiting_for_registration.add(user_id)
 await update.message.reply_text(
 "👋 Добро пожаловать!\n\n"
 "Для регистрации отправьте:\n\n"
 "ИМЯ ГРУППА\n\n"
 "Пример:\n"
 "Иван ИС-21"
 )
 else:
 await update.message.reply_text(
 "👋 С возвращением!",
 reply_markup=keyboard
 )
 except Exception as e:
 print(f"❌ Ошибка: {e}")
 await update.message.reply_text("❌ Ошибка БД")
 finally:
 conn.close()

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
 user_id = update.message.from_user.id
 msg = update.message.text
 conn = get_connection()
 if not conn:
 await update.message.reply_text("❌ Ошибка подключения к БД")
 return
 
 try:
 cursor = conn.cursor()
 
 if user_id in waiting_for_registration:
 try:
 data = msg.split()
 name = data[0]
 group_name = data[1]
 cursor.execute(
 "INSERT INTO users VALUES (%s, %s, %s)",
 (user_id, name, group_name)
 )
 conn.commit()
 waiting_for_registration.remove(user_id)
 await update.message.reply_text(
 f"✅ Регистрация завершена!\n\n"
 f"👤 Имя: {name}\n"
 f"📚 Группа: {group_name}",
 reply_markup=keyboard
 )
 except:
 await update.message.reply_text(
 "❌ Неверный формат.\n\n"
 "Пример:\n"
 "Иван ИС-21"
 )
 cursor.close()
 return
 
 if user_id in waiting_for_consultation:
 waiting_for_consultation.remove(user_id)
 await update.message.reply_text(
 "✅ Вы успешно записаны на консультацию!"
 )
 await context.bot.send_message(
 chat_id=ADMIN_ID,
 text=
 f"📥 Новая запись на консультацию!\n\n"
 f"{msg}"
 )
 cursor.close()
 return
 
 if msg == "📅 Расписание":
 cursor.execute(
 "SELECT group_name FROM users WHERE user_id=%s",
 (user_id,)
 )
 result = cursor.fetchone()
 if result:
 group_name = result[0]
 text = schedule.get(
 group_name,
 "❌ Расписание не найдено"
 )
 await update.message.reply_text(text)
 elif msg == "⏰ Ближайшая пара":
 await update.message.reply_text(
 "⏰ Следующая пара:\n\n"
 "📘 Математика\n"
 "🕒 10:00\n"
 "🏫 Кабинет 305"
 )
 elif msg == "📝 Домашка":
 await update.message.reply_text(
 "📝 Домашние задания:\n\n"
 "📘 Математика — No25\n"
 "📗 История — реферат\n"
 "📙 Английский — стр. 15"
 )
 elif msg == "🏆 Оценки":
 await update.message.reply_text(
 "🏆 Ваши оценки:\n\n"
 "📘 Математика — 5\n"
 "📗 История — 4\n"
 "📙 Английский — 5"
 )
 elif msg == "👨‍🏫 Консультация":
 waiting_for_consultation.add(user_id)
 await update.message.reply_text(
 "📝 Отправьте одним сообщением:\n\n"
 "• ФИО\n"
 "• Предмет\n"
 "• Время"
 )
 elif msg == "📅 Экзамены":
 await update.message.reply_text(
 "📅 Ближайшие экзамены:\n\n"
 "📘 Математика — 25 июня\n"
 "📗 Физика — 28 июня"
 )
 elif msg == "📚 Материалы":
 await update.message.reply_text(
 "📚 Учебные материалы:\n\n"
 "📄 Лекции\n"
 "📄 Презентации\n"
 "📄 Методички"
 )
 elif msg == "📢 Новости":
 await update.message.reply_text(
 "📢 Новости колледжа:\n\n"
 "🎉 День студента — 20 мая\n"
 "📚 Сессия начинается 1 июня"
 )
 elif msg == "💰 Стипендия":
 await update.message.reply_text(
 "💰 Стипендии:\n\n"
 "📌 Обычная — 5000₽\n"
 "📌 Повышенная — 9000₽"
 )
 elif msg == "🏫 Кабинеты":
 await update.message.reply_text(
 "🏫 Кабинеты:\n\n"
 "305 — Математика\n"
 "204 — Деканат\n"
 "101 — Библиотека"
 )
 elif msg == "👤 Мой профиль":
 cursor.execute(
 "SELECT name, group_name FROM users WHERE user_id=%s",
 (user_id,)
 )
 user = cursor.fetchone()
 if user:
 await update.message.reply_text(
 f"👤 Имя: {user[0]}\n"
 f"📚 Группа: {user[1]}"
 )
 elif msg == "📞 Контакты":
 await update.message.reply_text(
 "📞 Контакты:\n\n"
 "☎️ Деканат: +7 8662 49-61-51\n"
 "📧 https://nalchik.top-academy.ru/"
 )
 elif msg == "❓ Помощь":
 await update.message.reply_text(
 "📞 Обратитесь в деканат."
 )
 else:
 await update.message.reply_text(
 "❗ Используйте кнопки меню"
 )
 
 except Exception as e:
 print(f"❌ Ошибка: {e}")
 await update.message.reply_text("❌ Ошибка БД")
 finally:
 cursor.close()
 conn.close()

if __name__ == "__main__":
 init_db()
 app = ApplicationBuilder().token(TOKEN).build()
 app.add_handler(
 CommandHandler("start", start)
 )
 app.add_handler(
 MessageHandler(filters.TEXT, buttons)
 )
 print("✅ Бот запущен...")
 app.run_polling()
