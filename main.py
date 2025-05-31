from telegram.ext import Updater, CommandHandler

def start(update, context):
    pass  # Пока ничего не делает

def main():
    TOKEN = '8196984264:AAE4Y3f_RpzmoPN-s6iXJhgA72bVoXiZCoM'
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
