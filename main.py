import json
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")

NAME, PHONE, LOCATION = range(3)

DATA_FILE = "members.json"


def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🙏 Welcome to Bible & Coffee!\n\nWhat is your full name?"
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("📞 Please enter your phone number:")
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("📍 Which area/location are you in?")
    return LOCATION


async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.text
    name = context.user_data["name"]
    phone = context.user_data["phone"]

    data = load_data()

    if location not in data:
        data[location] = []

    groups = data[location]

    assigned_group = None

    for i, group in enumerate(groups):
        if len(group) < 8:
            assigned_group = i
            break

    if assigned_group is None:
        groups.append([])
        assigned_group = len(groups) - 1

    member = {
        "name": name,
        "phone": phone,
        "telegram_id": update.effective_user.id
    }

    groups[assigned_group].append(member)

    save_data(data)

    await update.message.reply_text(
        f"✅ You are registered!\n\n"
        f"📍 Location: {location}\n"
        f"👥 Group: Cell {assigned_group + 1}\n"
        f"📊 Members: {len(groups[assigned_group])}/8\n\n"
        f"God bless you 🙏"
    )

    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_location)],
        },
    )

    app.add_handler(conv)

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
