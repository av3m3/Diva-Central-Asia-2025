import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from fastapi import FastAPI, Request
import uvicorn

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Бот работает через webhook.")

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_DOMAIN = os.getenv("WEBHOOK_DOMAIN")

if not TELEGRAM_TOKEN or not WEBHOOK_DOMAIN:
    raise RuntimeError("TELEGRAM_TOKEN или WEBHOOK_DOMAIN не заданы!")

WEBHOOK_PATH = f"/{TELEGRAM_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_DOMAIN}{WEBHOOK_PATH}"

application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
application.add_handler(CommandHandler("start", start))

@app.on_event("startup")
async def on_startup():
    print(f"Устанавливаем webhook: {WEBHOOK_URL}")
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
