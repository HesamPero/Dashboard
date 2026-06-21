"""
Mahdieh's Travel Map — Telegram Bot
Password protected + personalized
"""
import os, logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, ContextTypes, filters
)
from travel_data import all_places, add_place, update_status, delete_place, upload_photo, update_photo_url, geocode

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
PASSWORD = "mahdieh"

ASK_CITY, ASK_STATUS, ASK_NOTE, ASK_PHOTO = range(4)

# Authorized user IDs (saved in memory — persists while bot runs)
authorized_users: set = set()


def is_authorized(user_id: int) -> bool:
    return user_id in authorized_users


async def require_auth(update: Update) -> bool:
    """Returns True if authorized, False and sends message if not."""
    if is_authorized(update.effective_user.id):
        return True
    await update.message.reply_text(
        "🔐 This is a private app.\n\nPlease send the password to continue 🌸"
    )
    return False


async def handle_password(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Check if message is the password."""
    if update.message.text.strip() == PASSWORD:
        authorized_users.add(update.effective_user.id)
        await update.message.reply_text(
            f"✨ Welcome, Mahdieh! 🌸\n\n"
            f"This is your personal travel map — built just for you with love 💕\n\n"
            f"📍 /add — add a new place\n"
            f"🌍 /list — see all your places\n"
            f"🌙 /dreams — places you want to go\n"
            f"✓ /visited — places you've been\n"
            f"❓ /help — how to use this bot"
        )
    else:
        await update.message.reply_text("That's not the right password. Try again 🌸")


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if is_authorized(update.effective_user.id):
        await update.message.reply_text(
            "🌸 *Mahdieh's Travel Map* 🌸\n\n"
            "Your personal travel list — dreams and memories 🗺️\n\n"
            "📍 /add — add a new place\n"
            "🌍 /list — see all your places\n"
            "🌙 /dreams — places you want to go\n"
            "✓ /visited — places you've been\n"
            "❓ /help — how to use this bot",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "🔐 This is a private app made with love 💕\n\nPlease send the password to continue 🌸"
        )


async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await require_auth(update): return
    await update.message.reply_text(
        "*How to use Mahdieh's Travel Map:*\n\n"
        "• /add — add a place step by step\n"
        "• /list — see everything on your map\n"
        "• /dreams — dream destinations 🌙\n"
        "• /visited — places you've been ✓\n\n"
        "Everything syncs with the web map instantly! 🌸",
        parse_mode="Markdown"
    )


async def add_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await require_auth(update): return ConversationHandler.END
    await update.message.reply_text("📍 *Adding a new place*\n\nWhat's the city or place?", parse_mode="Markdown")
    return ASK_CITY


async def ask_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    ctx.user_data["city_input"] = city
    await update.message.reply_text("Looking it up… 🔍")
    geo = geocode(city)
    if geo is None:
        await update.message.reply_text("Couldn't find that place. Try a different spelling?\n\nOr /cancel to stop.")
        return ASK_CITY
    ctx.user_data["geo"] = geo
    keyboard = [[
        InlineKeyboardButton("🌙 Dream — I want to go", callback_data="dream"),
        InlineKeyboardButton("✓ Visited — I've been", callback_data="visited"),
    ]]
    await update.message.reply_text(
        f"Found *{geo['name']}*, {geo['country']} 🌍\n\nDream or visited?",
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )
    return ASK_STATUS


async def ask_note(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    ctx.user_data["status"] = query.data
    label = "dream destination 🌙" if query.data == "dream" else "visited place ✓"
    await query.edit_message_text(f"Marked as *{label}*.\n\nAdd a note? Or /skip.", parse_mode="Markdown")
    return ASK_NOTE


async def ask_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["note"] = update.message.text.strip()
    await update.message.reply_text("📷 Send a photo, or /skip to finish.")
    return ASK_PHOTO


async def skip_note(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["note"] = ""
    await update.message.reply_text("📷 Send a photo, or /skip to finish.")
    return ASK_PHOTO


async def finish_with_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    geo = ctx.user_data["geo"]
    status = ctx.user_data["status"]
    note = ctx.user_data.get("note", "")
    await update.message.reply_text("Uploading photo… ☁️")
    photo = update.message.photo[-1]
    file = await ctx.bot.get_file(photo.file_id)
    photo_bytes = await file.download_as_bytearray()
    entry = add_place(name=geo["name"], country=geo["country"], lat=geo["lat"], lon=geo["lon"], status=status, note=note)
    photo_url = upload_photo(bytes(photo_bytes), entry["id"])
    if photo_url:
        update_photo_url(entry["id"], photo_url)
    emoji = "🌙" if status == "dream" else "✓"
    await update.message.reply_text(
        f"{emoji} *{geo['name']}* added to your map, Mahdieh! 🌸\n_{geo['country']}_\n📷 Photo saved!",
        parse_mode="Markdown"
    )
    ctx.user_data.clear()
    return ConversationHandler.END


async def finish_no_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    geo = ctx.user_data["geo"]
    status = ctx.user_data["status"]
    note = ctx.user_data.get("note", "")
    add_place(name=geo["name"], country=geo["country"], lat=geo["lat"], lon=geo["lon"], status=status, note=note)
    emoji = "🌙" if status == "dream" else "✓"
    await update.message.reply_text(
        f"{emoji} *{geo['name']}* added to your map, Mahdieh! 🌸\n_{geo['country']}_",
        parse_mode="Markdown"
    )
    ctx.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    await update.message.reply_text("Cancelled. Use /add anytime 🌸")
    return ConversationHandler.END


def format_place(p):
    emoji = "🌙" if p["status"] == "dream" else "✓"
    text = f"{emoji} *{p['name']}* — {p['country']}\n"
    if p.get("note"): text += f"  _{p['note']}_\n"
    if p.get("photo_url"): text += f"  📷 [View photo]({p['photo_url']})\n"
    text += f"  ID: `{p['id']}`\n"
    return text


async def list_places(update, ctx, filter_status=None):
    if not await require_auth(update): return
    places = all_places()
    if filter_status:
        places = [p for p in places if p["status"] == filter_status]
    if not places:
        label = {"dream": "dream destinations", "visited": "visited places"}.get(filter_status, "places")
        await update.message.reply_text(f"No {label} yet — use /add to start 🌸")
        return
    label = {"dream": "🌙 Dream Destinations", "visited": "✓ Places Visited"}.get(filter_status, "🗺️ All Your Places")
    current = f"*{label}* ({len(places)} total)\n\n"
    for p in reversed(places):
        line = format_place(p)
        if len(current) + len(line) > 3800:
            await update.message.reply_text(current, parse_mode="Markdown", disable_web_page_preview=True)
            current = line
        else:
            current += line
    keyboard = [[
        InlineKeyboardButton("Mark visited ✓", callback_data="action_mark"),
        InlineKeyboardButton("Remove 🗑", callback_data="action_remove"),
    ]]
    await update.message.reply_text(
        current, parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def cmd_list(update, ctx): await list_places(update, ctx)
async def cmd_dreams(update, ctx): await list_places(update, ctx, "dream")
async def cmd_visited(update, ctx): await list_places(update, ctx, "visited")


async def action_callback(update, ctx):
    query = update.callback_query
    await query.answer()
    if query.data == "action_mark":
        await query.message.reply_text("Send me the ID of the place to mark as visited.")
        ctx.user_data["pending_action"] = "mark"
    elif query.data == "action_remove":
        await query.message.reply_text("Send me the ID of the place to remove.")
        ctx.user_data["pending_action"] = "remove"


async def handle_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    # Check pending action first
    action = ctx.user_data.get("pending_action")
    if action:
        place_id = update.message.text.strip()
        places = all_places()
        match = next((p for p in places if p["id"] == place_id), None)
        if not match:
            await update.message.reply_text("Couldn't find that ID. Check /list and try again.")
            ctx.user_data.clear()
            return
        if action == "mark":
            update_status(place_id, "visited")
            await update.message.reply_text(f"✓ *{match['name']}* marked as visited! 🌸", parse_mode="Markdown")
        elif action == "remove":
            delete_place(place_id)
            await update.message.reply_text(f"Removed *{match['name']}* from your map.", parse_mode="Markdown")
        ctx.user_data.clear()
        return

    # Check if it's a password attempt
    if not is_authorized(update.effective_user.id):
        await handle_password(update, ctx)
        return

    await update.message.reply_text("Use /add to add a place, or /list to see your map 🌸")


def main():
    if not BOT_TOKEN:
        print("⚠️  Set TELEGRAM_BOT_TOKEN!")
        return
    app = Application.builder().token(BOT_TOKEN).build()
    add_conv = ConversationHandler(
        entry_points=[CommandHandler("add", add_start)],
        states={
            ASK_CITY:   [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_status)],
            ASK_STATUS: [CallbackQueryHandler(ask_note, pattern="^(dream|visited)$")],
            ASK_NOTE:   [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_photo), CommandHandler("skip", skip_note)],
            ASK_PHOTO:  [MessageHandler(filters.PHOTO, finish_with_photo), CommandHandler("skip", finish_no_photo)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("list", cmd_list))
    app.add_handler(CommandHandler("dreams", cmd_dreams))
    app.add_handler(CommandHandler("visited", cmd_visited))
    app.add_handler(add_conv)
    app.add_handler(CallbackQueryHandler(action_callback, pattern="^action_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("🌸 Mahdieh's Travel Map bot is running…")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
