import os
from dotenv import load_dotenv
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes, filters
)
from fastapi import FastAPI, Request
import uvicorn

load_dotenv()

AWAITING_ANSWERS, AWAITING_PHOTOS = range(2)
ADMIN_CHAT_ID = 1870625035
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScfK-ItvQQhK4cfG2pymvApwGymnAkgI2c8ibOjWLfBgfFSiA/viewform?usp=header"
PDF_PATH = "DIVA CENTRAL ASIA 25- РЕГЛАМЕНТ.pdf"

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📝 Регламент конкурса", callback_data='regulations')],
        [InlineKeyboardButton("✏️ Анкета участника", callback_data='participant_form')],
        [InlineKeyboardButton("🎥 Заявка на участие", callback_data='participation_application')],
        [InlineKeyboardButton("⚙️ Дополнительная информация", callback_data='additional_info')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выберите пункт меню:", reply_markup=get_main_menu())
    context.user_data.pop('regulation_message_id', None)

async def show_regulations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.message.delete()
    except: pass
    with open(PDF_PATH, 'rb') as pdf_file:
        sent_message = await query.message.chat.send_document(document=pdf_file)
    context.user_data['regulation_message_id'] = sent_message.message_id
    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data='back_to_menu')]]
    await query.message.chat.send_message("📄 Ознакомьтесь с регламентом:", reply_markup=InlineKeyboardMarkup(keyboard))

async def participant_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📝 Перейти к анкете", url=GOOGLE_FORM_URL)],
        [InlineKeyboardButton("⬅️ Назад", callback_data='back_to_menu')]
    ]
    await query.edit_message_text("✏️ Заполните анкету по ссылке:", reply_markup=InlineKeyboardMarkup(keyboard))

async def additional_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "✨ <b>Остались вопросы? Мы всегда на связи!</b>\n\n"
        "📞 <b>Телефон:</b> +7 776 121 76 71\n"
        "💬 <b>Telegram:</b> @Simon_dj_Simon\n"
        "📸 <b>Instagram:</b> <a href='https://www.instagram.com/central_station_astana?igsh=MWJqdnFwbDZmeHlocg'>@central_station_astana</a>"
    )
    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data='back_to_menu')]]
    await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        if 'regulation_message_id' in context.user_data:
            await query.message.chat.delete_message(context.user_data['regulation_message_id'])
            context.user_data.pop('regulation_message_id')
        await query.message.delete()
    except: pass
    await query.message.chat.send_message('Выберите пункт меню:', reply_markup=get_main_menu())

async def participation_application(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "📌 Ответьте одним сообщением на:\n\n"
        "1️⃣ Имя и фамилия\n2️⃣ Псевдоним\n3️⃣ Возраст\n4️⃣ Город\n"
        "5️⃣ Опыт\n6️⃣ Репертуар\n7️⃣ Телефон и email\n\n"
        "Затем отправьте 3–4 фото."
    )
    await query.message.reply_text(text)
    return AWAITING_ANSWERS

async def receive_answers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['answers'] = update.message.text
    context.user_data['photos'] = []
    await update.message.reply_text("Ответы получены. Отправьте 3–4 фотографии.")
    return AWAITING_PHOTOS

async def receive_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photos = context.user_data.get('photos', [])
    photos.append(update.message.photo[-1].file_id)
    context.user_data['photos'] = photos

    if len(photos) >= 3:
        keyboard = [[InlineKeyboardButton("Сохранить заявку", callback_data='save_registration')]]
        await update.message.reply_text(f"Фото получено ({len(photos)}). Нажмите кнопку ниже:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(f"Фото получено ({len(photos)}). Отправьте ещё.")
    return AWAITING_PHOTOS

async def save_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    answers = context.user_data.get('answers')
    photos = context.user_data.get('photos', [])
    if not answers or len(photos) < 3:
        await query.answer("Нужно минимум 3 фото и текст!", show_alert=True)
        return AWAITING_PHOTOS
    user = query.from_user
    await context.bot.send_message(ADMIN_CHAT_ID, f"Заявка от @{user.username or user.full_name}:\n\n{answers}")
    await context.bot.send_media_group(ADMIN_CHAT_ID, [InputMediaPhoto(p) for p in photos])
    await query.edit_message_text("Заявка отправлена организаторам! Спасибо.")
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Регистрация отменена.")
    context.user_data.clear()
    return ConversationHandler.END

# ---- FastAPI + Webhook часть ----

app = FastAPI()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_DOMAIN = os.getenv("WEBHOOK_DOMAIN")
WEBHOOK_PATH = f"/{TELEGRAM_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_DOMAIN}{WEBHOOK_PATH}"

application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

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

application.add_handler(CommandHandler("start", start))
application.add_handler(conv_handler)
application.add_handler(CallbackQueryHandler(show_regulations, pattern='regulations'))
application.add_handler(CallbackQueryHandler(participant_form, pattern='participant_form'))
application.add_handler(CallbackQueryHandler(additional_info, pattern='additional_info'))
application.add_handler(CallbackQueryHandler(back_to_menu, pattern='back_to_menu'))

@app.on_event("startup")
async def on_startup():
    await application.initialize()
    print(f"Webhook устанавливается: {WEBHOOK_URL}")
    await application.bot.set_webhook(WEBHOOK_URL)

@app.post(WEBHOOK_PATH)
async def process_update(request: Request):
    json_data = await request.json()
    update = Update.de_json(json_data, application.bot)
    await application.process_update(update)
    return "ok"

def main():
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
