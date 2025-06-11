import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters, CallbackQueryHandler
)
from openai import OpenAI
from database import add_user  # تابع ذخیره کاربر

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)

# اتصال به OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# حافظه موقت کاربران ناشناس
waiting_users = []
chat_pairs = {}

# ⬅️ دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # ذخیره اطلاعات کاربر در دیتابیس
    add_user(user.id, user.username or "")

    keyboard = [
        [InlineKeyboardButton("🔍 جستجوی ناشناس", callback_data="search")],
        [InlineKeyboardButton("🤖 سوال از هوش مصنوعی", callback_data="ai")],
        [InlineKeyboardButton("❌ خروج", callback_data="exit")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! یکی از گزینه‌ها رو انتخاب کن:", reply_markup=reply_markup)

# ⬅️ مدیریت دکمه‌ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "search":
        if user_id not in waiting_users:
            waiting_users.append(user_id)
            await query.edit_message_text("منتظر یک شخص برای چت هستید...")

        if len(waiting_users) >= 2:
            u1 = waiting_users.pop(0)
            u2 = waiting_users.pop(0)
            chat_pairs[u1] = u2
            chat_pairs[u2] = u1
            await context.bot.send_message(chat_id=u1, text="شما به چت ناشناس وصل شدید!")
            await context.bot.send_message(chat_id=u2, text="شما به چت ناشناس وصل شدید!")

    elif query.data == "exit":
        if user_id in chat_pairs:
            partner = chat_pairs.pop(user_id)
            chat_pairs.pop(partner, None)
            await context.bot.send_message(chat_id=user_id, text="شما از چت خارج شدید.")
            await context.bot.send_message(chat_id=partner, text="طرف مقابل چت را ترک کرد.")
        elif user_id in waiting_users:
            waiting_users.remove(user_id)
            await context.bot.send_message(chat_id=user_id, text="از صف انتظار خارج شدید.")
        else:
            await context.bot.send_message(chat_id=user_id, text="شما در هیچ چتی نیستید.")

    elif query.data == "ai":
        context.user_data["ai_mode"] = True
        await context.bot.send_message(chat_id=user_id, text="پیام خود را بفرست تا از هوش مصنوعی بپرسم.")

# ⬅️ مدیریت پیام‌ها
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if context.user_data.get("ai_mode"):
        await update.message.reply_text("🔄 در حال دریافت پاسخ از هوش مصنوعی...")

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": text}]
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = "❌ خطا در ارتباط با هوش مصنوعی."

        await update.message.reply_text(reply)
        context.user_data["ai_mode"] = False
        return

    if user_id in chat_pairs:
        partner_id = chat_pairs[user_id]
        await context.bot.send_message(chat_id=partner_id, text=text)
    else:
        await update.message.reply_text("شما در حال حاضر در چت نیستید یا گزینه‌ای انتخاب نکرده‌اید.")

# ⬅️ اجرای بات
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
