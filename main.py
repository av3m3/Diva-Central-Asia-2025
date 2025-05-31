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

AWAITING_ANSWERS, AWAITING_PHOTOS = range(2)

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 1870625035  # Замените на ваш ID

# --- Здесь твои все async функции-хендлеры, как в твоём коде ---
# start, show_regulations, participant_form, additional_info, back_to_menu,
# participation_application, receive_answers, receive_photos,
# save_registration, cancel

# Ниже для примера покажу только один, остальные вставь свои без изменений:

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text('Выберите пункт меню:', reply_markup=get_main_menu())
        context.user_data.pop('regulation_message_id', None)
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        if 'regulation_message_id' in context.user_data:
            try:
                await query.message.chat.delete_message(context.user_data['regulation_message_id'])
            except Exception:
                pass
            context.user_data.pop('regulation_message_id')

        await query.edit_message_text('Выберите пункт меню:', reply_markup=get_main_menu())

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📝 Регламент конкурса", callback_data='regulations')],
        [InlineKeyboardButton("✏️ Анкета участника", callback_data='participant_form')],
        [InlineKeyboardButton("🎥 Заявка на участие", callback_data='participation_application')],
        [InlineKeyboardButton("⚙️ Дополнительная информация", callback_data='additional_info')]
    ]
    return InlineKeyboardMarkup(keyboard)

app_api = FastAPI()

@app_api.get("/health")
async def health():
    return {"status": "ok"}

def run_webserver():
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app_api, host="0.0.0.0", port=port)

def main():
    # Запускаем веб-сервер в отдельном потоке (чтобы Render видел прослушиваемый порт)
    threading.Thread(target=run_webserver, daemon=True).start()

    # Строим и запускаем Telegram-бота
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
