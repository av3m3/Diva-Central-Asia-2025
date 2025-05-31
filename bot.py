from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes, filters
)

AWAITING_ANSWERS, AWAITING_PHOTOS = range(2)

TOKEN = '8196984264:AAE4Y3f_RpzmoPN-s6iXJhgA72bVoXiZCoM'
ADMIN_CHAT_ID = 1870625035  # Замените на ваш ID

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📝 Регламент конкурса", callback_data='regulations')],
        [InlineKeyboardButton("✏️ Анкета участника", callback_data='participant_form')],
        [InlineKeyboardButton("🎥 Заявка на участие", callback_data='participation_application')],
        [InlineKeyboardButton("⚙️ Дополнительная информация", callback_data='additional_info')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def show_regulations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    pdf_path = "DIVA CENTRAL ASIA 25- РЕГЛАМЕНТ.pdf"

    try:
        await query.message.delete()
    except Exception:
        pass

    with open(pdf_path, 'rb') as pdf_file:
        sent_message = await query.message.chat.send_document(
            document=pdf_file,
            filename="DIVA CENTRAL ASIA 25- РЕГЛАМЕНТ.pdf"
        )
    context.user_data['regulation_message_id'] = sent_message.message_id

    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data='back_to_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.chat.send_message(
        "📄 Вот регламент конкурса. Пожалуйста, ознакомьтесь с документом.\nЕсли хотите вернуться в меню — нажмите кнопку ниже.",
        reply_markup=reply_markup
    )

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

GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScfK-ItvQQhK4cfG2pymvApwGymnAkgI2c8ibOjWLfBgfFSiA/viewform?usp=header"

async def participant_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📝 Перейти к анкете", url=GOOGLE_FORM_URL)],
        [InlineKeyboardButton("⬅️ Назад", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="✏️ Чтобы подать заявку на участие, заполните анкету по кнопке ниже:",
        reply_markup=reply_markup
    )

async def additional_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data='back_to_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        "✨ <b>Остались вопросы? Мы всегда на связи!</b>\n\n"
        "📞 <b>Телефон / WhatsApp:</b> +7 776 121 76 71\n"
        "💬 <b>Telegram:</b> @Simon_dj_Simon\n"
        "📸 <b>Instagram:</b> <a href='https://www.instagram.com/central_station_astana?igsh=MWJqdnFwbDZmeHlocg'>@central_station_astana</a>\n\n"
        "💖 Напиши нам — и мы с удовольствием ответим на всё, "
        "что волнует тебя перед выходом на сцену!"
    )
    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='HTML')

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if 'regulation_message_id' in context.user_data:
        try:
            await query.message.chat.delete_message(context.user_data['regulation_message_id'])
        except Exception:
            pass
        context.user_data.pop('regulation_message_id')

    try:
        await query.message.delete()
    except Exception:
        pass

    await query.message.chat.send_message('Выберите пункт меню:', reply_markup=get_main_menu())

async def participation_application(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "📌 Пожалуйста, ответьте одним сообщением на следующие вопросы:\n\n"
        "1️⃣ Имя и фамилия по документам\n"
        "2️⃣ Сценический псевдоним\n"
        "3️⃣ Возраст\n"
        "4️⃣ Страна, город\n"
        "5️⃣ Опыт публичных выступлений\n"
        "6️⃣ Репертуар для конкурса\n"
        "7️⃣ Контактные данные: номер телефона и email\n\n"
        "После отправки текста пришлите 3–4 фотографии в образе."
    )
    await query.message.reply_text(text)
    return AWAITING_ANSWERS

async def receive_answers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['answers'] = update.message.text
    context.user_data['photos'] = []
    await update.message.reply_text("Текст получен! Теперь отправьте 3–4 фотографии в образе.")
    return AWAITING_PHOTOS

async def receive_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photos = context.user_data.get('photos', [])
    photos.append(update.message.photo[-1].file_id)
    context.user_data['photos'] = photos

    if len(photos) >= 3:
        keyboard = [[InlineKeyboardButton("Сохранить заявку", callback_data='save_registration')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"Фото получено ({len(photos)}/4). Можно отправить ещё или нажмите «Сохранить заявку».",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(f"Фото получено ({len(photos)}/4). Отправьте ещё фото.")
    return AWAITING_PHOTOS

async def save_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    answers = context.user_data.get('answers')
    photos = context.user_data.get('photos', [])

    if not answers:
        await query.answer("Сначала отправьте текст с ответами.", show_alert=True)
        return AWAITING_ANSWERS

    if len(photos) < 3:
        await query.answer("Отправьте минимум 3 фотографии.", show_alert=True)
        return AWAITING_PHOTOS

    user = query.from_user
    header = f"Новая заявка от @{user.username or user.full_name}:\n\n"
    await context.bot.send_message(ADMIN_CHAT_ID, header + answers)

    media = [InputMediaPhoto(file_id) for file_id in photos]
    await context.bot.send_media_group(ADMIN_CHAT_ID, media)

    await query.edit_message_text("Ваша заявка отправлена организаторам! Спасибо!")
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Регистрация отменена.")
    context.user_data.clear()
    return ConversationHandler.END

def get_application(token: str):
    app = ApplicationBuilder().token(token).build()

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

    return app

# Если хочешь запускать polling локально — раскомментируй ниже
# async def main():
#     app = get_application(TOKEN)
#     await app.run_polling()
#
# if __name__ == '__main__':
#     import asyncio
#     asyncio.run(main())
