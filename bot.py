import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler

# --- КОНФИГУРАЦИЯ ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8163012748:AAHWr2d6sS1uhrRIHeRBc223Jr67ljKY-0U")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyA3S3xng4XjGuMP9_wDUIqattw8jEBfqTo")

# Gemini баптау
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- МҰҒАЛІМ ТУРАЛЫ МӘЛІМЕТ ---
TEACHER_INFO = """
Сен — Қорқыт ағайдың мұғалім көмекші боты.

Мұғалім туралы:
- Аты-жөні: Жәли Қорқыт Жеңісұлы
- Туған жылы: 1994 жыл, Ажар ауылы
- Білімі: Еуразия ұлттық университеті
- Жұмыс орны: №23 мектеп-лицей
- Пәні: Математика (математикадан сабақ береді)
- Жанкүйер: Реал Мадрид командасы

Сенің міндетің:
1. Оқушылар мен ата-аналармен қазақ тілінде сөйлес
2. Математика сұрақтарына жауап бер
3. Оқушыларды МОТИВАЦИЯЛАП, қолдап отыр
4. Ата-аналарға балалары туралы кеңес бер
5. Достық, жылы, ақылды бол
6. Қорқыт ағай туралы сұраса — жоғарыдағы мәліметтерді айт
7. Жауаптарың қысқа, анық, ынталандырушы болсын
8. Эмодзи қолдан, жылы тіл қолдан
9. Егер оқушы уайымдаса — мотивация бер, сенім арт
10. Тек қазақ тілінде жауап бер (орысша жазса да қазақша жауап бер)
"""

# Әр пайдаланушының чат тарихы
user_sessions = {}

# --- /start командасы ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name or "Сәлем"
    welcome_text = (
        f"Сәлем, {user_name}! 👋\n\n"
        f"Мен — Қорқыт ағайдың көмекші боты 🤖\n\n"
        f"📚 Математика сұрақтарыңды қой\n"
        f"💪 Мотивация керек пе? Жаз!\n"
        f"👨‍👩‍👧 Ата-аналар да жаза алады\n\n"
        f"Қандай сұрағың бар? ✨"
    )
    await update.message.reply_text(welcome_text)

# --- Хабарламаларға жауап ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    # Пайдаланушы сессиясын жасау
    if user_id not in user_sessions:
        user_sessions[user_id] = model.start_chat(history=[])

    chat = user_sessions[user_id]

    # Gemini-ге сұраныс жібер
    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )

        full_prompt = f"{TEACHER_INFO}\n\nОқушы/Ата-ана хабарламасы: {user_text}"
        response = chat.send_message(full_prompt)
        reply = response.text

        await update.message.reply_text(reply)

    except Exception as e:
        logger.error(f"Қате: {e}")
        await update.message.reply_text(
            "Кешіріңіз, қазір қиындық туды 😔 Біраздан кейін қайта жазыңыз."
        )

# --- MAIN ---
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Бот іске қосылды ✅")
    app.run_polling()

if __name__ == "__main__":
    main()
