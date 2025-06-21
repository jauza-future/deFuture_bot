from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
import sqlite3

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

conn = sqlite3.connect('referral.db', check_same_thread=False)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    referred_by INTEGER
)
''')
conn.commit()

app = FastAPI()
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

    referred_by = None
    if args:
        try:
            referred_by = int(args[0])
        except ValueError:
            referred_by = None

    c.execute('SELECT * FROM users WHERE user_id = ?', (user.id,))
    if c.fetchone() is None:
        c.execute('INSERT INTO users (user_id, username, referred_by) VALUES (?, ?, ?)',
                  (user.id, user.username, referred_by))
        conn.commit()
        await update.message.reply_text(f"Halo {user.first_name}! Kamu sudah terdaftar.")
        if referred_by:
            await update.message.reply_text(f"Kamu direferensikan oleh ID {referred_by}.")
    else:
        await update.message.reply_text("Kamu sudah terdaftar sebelumnya.")

    bot_username = (await context.bot.get_me()).username
    referral_link = f"https://t.me/{bot_username}?start={user.id}"
    await update.message.reply_text(f"Bagikan link referral kamu: {referral_link}")

async def referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    c.execute('SELECT user_id, username FROM users WHERE referred_by = ?', (user.id,))
    results = c.fetchall()

    if results:
        msg = "Orang yang kamu referensikan:\n"
        for r in results:
            uname = r[1] if r[1] else 'Tanpa username'
            msg += f"- {uname} (ID: {r[0]})\n"
    else:
        msg = "Belum ada yang kamu referensikan."

    await update.message.reply_text(msg)

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("referrals", referrals))

@app.post("/")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    await bot_app.bot.set_webhook(WEBHOOK_URL)
