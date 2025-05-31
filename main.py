import os
from telegram.ext import Updater, CommandHandler

def start(update, context):
    pass  # Пока ничего не делает

def main():
    TOKEN = os.environ.get("TELEGRAM_TOKEN")  # ← читаем из окружения
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
