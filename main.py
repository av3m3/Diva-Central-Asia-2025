import os
import threading
from fastapi import FastAPI
import uvicorn

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes, filters
)

# ... Твой код с хендлерами и функциями без изменений ...

AWAITING_ANSWERS, AWAITING_PHOTOS = range(2)

TOKEN = '8196984264:AAE4Y3f_RpzmoPN-s6iXJhgA72bVoXiZCoM'
ADMIN_CHAT_ID = 1870625035  # Замените на ваш ID

# (Весь твой код функций сюда, без изменений)

app_api = FastAPI()

@app_api.get("/health")
async def health():
    return {"status": "ok"}

def run_webserver():
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app_api, host="0.0.0.0", port=port)

def main():
    # Запускаем FastAPI сервер в отдельном потоке, чтобы слушал порт
    threading.Thread(target=run_webserver, daemon=True).start()

    # Запускаем Telegram-бота, как обычно
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(participation_application, pattern='participation_application')],
        states={
            AWAITING_ANSWERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_answers)],
            AWAITING_PHOTOS: [
                MessageHandler(filters.PHOTO, receive_photos),
                CallbackQueryHandler(save_registration, pattern='save_registration')
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(CommandHandler('start', start))
    app.add_handler(conv_handler)

    app.add_handler(CallbackQueryHandler(show_regulations, pattern='regulations'))
    app.add_handler(CallbackQueryHandler(participant_form, pattern='participant_form'))
    app.add_handler(CallbackQueryHandler(additional_info, pattern='additional_info'))
    app.add_handler(CallbackQueryHandler(back_to_menu, pattern='back_to_menu'))

    app.run_polling()

if __name__ == '__main__':
    main()
