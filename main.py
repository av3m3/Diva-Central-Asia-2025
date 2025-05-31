import os
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен и работает!")

def main():
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        print("❌ TELEGRAM_TOKEN не найден в переменных окружения.")
        return

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == '__main__':
    main()
