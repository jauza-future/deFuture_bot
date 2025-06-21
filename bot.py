from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import sqlite3
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

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

def start(update: Update, context: CallbackContext):
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
        update.message.reply_text(f"Halo {user.first_name}! Kamu sudah terdaftar.")
        if referred_by:
            update.message.reply_text(f"Kamu direferensikan oleh ID {referred_by}.")
    else:
        update.message.reply_text("Kamu sudah terdaftar sebelumnya.")

    referral_link = f"https://t.me/{context.bot.username}?start={user.id}"
    update.message.reply_text(f"Bagikan link referral kamu: {referral_link}")

def referrals(update: Update, context: CallbackContext):
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

    update.message.reply_text(msg)

def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("referrals", referrals))

    print("Bot sudah berjalan. Tekan Ctrl+C untuk berhenti.")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
