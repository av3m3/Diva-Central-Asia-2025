import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackContext,
    CallbackQueryHandler, ConversationHandler
)
from fastapi import FastAPI, Request
import uvicorn

# Обработчики
async def start(update: Update, context: CallbackContext.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Бот работает через webhook.")

# FastAPI для Render
app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_DOMAIN = os.getenv("WEBHOOK_DOMAIN")  # Пример: https://your-bot.onrender.com
WEBHOOK_PATH = f"/{TELEGRAM_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_DOMAIN}{WEBHOOK_PATH}"

application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
application.add_handler(CommandHandler("start", start))

@app.on_event("startup")
async def on_startup():
    await application.bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook установлен: {WEBHOOK_URL}")

@app.post(WEBHOOK_PATH)
async def process_update(request: Request):
    json_data = await request.json()
    update = Update.de_json(json_data, application.bot)
    await application.process_update(update)
    return "ok"

def main():
    uvicorn.run("main:app", host="0.0.0.0", port=10000)

if __name__ == "__main__":
    main()
