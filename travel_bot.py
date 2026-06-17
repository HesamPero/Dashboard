"""
Her Travel Map — Telegram Bot
Run: python travel_bot.py
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, ContextTypes, filters
)
from travel_data import all_places, add_place, update_status, delete_place, save_photo, geocode

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Conversation states
ASK_CITY, ASK_STATUS, ASK_NOTE, ASK_PHOTO = range(4)


# ── /start ─────────────────────────────────────────────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✦ *Her Travel Map* ✦\n\n"
        "Your personal travel list — dreams and memories, all in one place.\n\n"
        "Commands:\n"
        "📍 /add — add a new place\n"
        "🌍 /list — see all your places\n"
        "🌙 /dreams — places you want to go\n"
        "✓ /visited — places you've been\n"
        "❓ /help — how to use this bot",
        parse_mode="Markdown"
    )


async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*How to use Her Travel Map:*\n\n"
        "• /add — start adding a new place (city name, dream or visited, a note, and optionally a photo)\n"
        "• /list — see everything on your map\n"
        "• /dreams — only your dream destinations 🌙\n"
        "• /visited — only places you've been ✓\n\n"
        "When browsing your list, you can mark a dream as visited, or remove a place.",
        parse_mode="Markdown"
    )


# ── Add flow ───────────────────────────────────────────────────────────────────
async def add_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📍 *Adding a new place*\n\nWhat's the name of the city or place?",
        parse_mode="Markdown"
    )
    return ASK_CITY


async def ask_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    ctx.user_data["city_input"] = city

    await update.message.reply_text("Looking it up… 🔍")
    geo = geocode(city)
    if geo is None:
        await update.message.reply_text(
            "I couldn't find that place on the map. Try a different spelling?\n\nOr /cancel to stop."
        )
        return ASK_CITY

    ctx.user_data["geo"] = geo
    keyboard = [[
        InlineKeyboardButton("🌙 Dream — I want to go", callback_data="dream"),
        InlineKeyboardButton("✓ Visited — I've been", callback_data="visited"),
    ]]
    await update.message.reply_text(
        f"Found *{geo['name']}*, {geo['country']} 🌍\n\nIs this a dream destination or somewhere you've visited?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return ASK_STATUS


async def ask_note(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    ctx.user_data["status"] = query.data  # "dream" or "visited"
    status_label = "dream destination 🌙" if query.data == "dream" else "visited place ✓"
    await query.edit_message_text(
        f"Marked as *{status_label}*.\n\nWant to add a note? (e.g. why you want to go, or a memory from there)\n\nOr send /skip to leave it blank.",
        parse_mode="Markdown"
    )
    return ASK_NOTE


async def ask_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    note = update.message.text.strip()
    ctx.user_data["note"] = "" if note.startswith("/skip") else note

    await update.message.reply_text(
        "📷 Want to add a photo? Send one now, or /skip to finish."
    )
    return ASK_PHOTO


async def skip_note(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["note"] = ""
    await update.message.reply_text(
        "📷 Want to add a photo? Send one now, or /skip to finish."
    )
    return ASK_PHOTO


async def finish_with_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    geo = ctx.user_data["geo"]
    status = ctx.user_data["status"]
    note = ctx.user_data.get("note", "")

    entry = add_place(
        name=geo["name"], country=geo["country"],
        lat=geo["lat"], lon=geo["lon"],
        status=status, note=note,
    )

    # Download and save photo
    photo = update.message.photo[-1]  # highest res
    file = await ctx.bot.get_file(photo.file_id)
    photo_bytes = await file.download_as_bytearray()
    save_photo(entry["id"], bytes(photo_bytes), "jpg")

    emoji = "🌙" if status == "dream" else "✓"
    await update.message.reply_text(
        f"{emoji} *{geo['name']}* added to your travel map with photo!\n\n"
        f"_{geo['country']}_",
        parse_mode="Markdown"
    )
    ctx.user_data.clear()
    return ConversationHandler.END


async def finish_no_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    geo = ctx.user_data["geo"]
    status = ctx.user_data["status"]
    note = ctx.user_data.get("note", "")

    add_place(
        name=geo["name"], country=geo["country"],
        lat=geo["lat"], lon=geo["lon"],
        status=status, note=note,
    )

    emoji = "🌙" if status == "dream" else "✓"
    await update.message.reply_text(
        f"{emoji} *{geo['name']}* added to your travel map!\n\n_{geo['country']}_",
        parse_mode="Markdown"
    )
    ctx.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    await update.message.reply_text("Cancelled. Use /add to start again anytime 🌿")
    return ConversationHandler.END


# ── List helpers ───────────────────────────────────────────────────────────────
def format_place(p: dict) -> str:
    emoji = "🌙" if p["status"] == "dream" else "✓"
    text = f"{emoji} *{p['name']}* — {p['country']}\n"
    if p.get("note"):
        text += f"  _{p['note']}_\n"
    text += f"  ID: `{p['id']}`\n"
    return text


async def list_places(update: Update, ctx: ContextTypes.DEFAULT_TYPE, filter_status=None):
    places = all_places()
    if filter_status:
        places = [p for p in places if p["status"] == filter_status]

    if not places:
        label = {"dream": "dream destinations", "visited": "visited places"}.get(filter_status, "places")
        await update.message.reply_text(f"No {label} yet — use /add to get started 🌿")
        return

    # Build message in chunks (Telegram limit 4096 chars)
    label = {"dream": "🌙 Dream Destinations", "visited": "✓ Places Visited"}.get(filter_status, "🗺️ All Your Places")
    header = f"*{label}* ({len(places)} total)\n\n"
    chunks = [header]
    current = header

    for p in reversed(places):
        line = format_place(p)
        if len(current) + len(line) > 3800:
            chunks.append(current)
            current = line
        else:
            current += line

    if current not in chunks:
        chunks.append(current)

    # Send all chunks; add action buttons on last
    for i, chunk in enumerate(chunks):
        if i == len(chunks) - 1:
            keyboard = [[
                InlineKeyboardButton("Mark a place as visited", callback_data="action_mark"),
                InlineKeyboardButton("Remove a place", callback_data="action_remove"),
            ]]
            await update.message.reply_text(
                chunk, parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text(chunk, parse_mode="Markdown")


async def cmd_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await list_places(update, ctx)

async def cmd_dreams(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await list_places(update, ctx, filter_status="dream")

async def cmd_visited(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await list_places(update, ctx, filter_status="visited")


# ── Inline actions (mark visited / remove) ─────────────────────────────────────
async def action_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "action_mark":
        await query.message.reply_text(
            "Send me the ID of the place you want to mark as visited.\n"
            "(IDs are shown in backticks in your list)"
        )
        ctx.user_data["pending_action"] = "mark"
    elif data == "action_remove":
        await query.message.reply_text(
            "Send me the ID of the place you want to remove."
        )
        ctx.user_data["pending_action"] = "remove"


async def handle_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    action = ctx.user_data.get("pending_action")
    if not action:
        await update.message.reply_text("Use /add to add a place, or /list to see your map 🌿")
        return

    place_id = update.message.text.strip()
    places = all_places()
    match = next((p for p in places if p["id"] == place_id), None)

    if not match:
        await update.message.reply_text("I couldn't find a place with that ID. Check /list and try again.")
        ctx.user_data.clear()
        return

    if action == "mark":
        update_status(place_id, "visited")
        await update.message.reply_text(f"✓ *{match['name']}* marked as visited!", parse_mode="Markdown")
    elif action == "remove":
        delete_place(place_id)
        await update.message.reply_text(f"Removed *{match['name']}* from your map.", parse_mode="Markdown")

    ctx.user_data.clear()


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("⚠️  Set your TELEGRAM_BOT_TOKEN environment variable first!")
        print("   export TELEGRAM_BOT_TOKEN=your_token_here")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    add_conv = ConversationHandler(
        entry_points=[CommandHandler("add", add_start)],
        states={
            ASK_CITY:   [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_status)],
            ASK_STATUS: [CallbackQueryHandler(ask_note, pattern="^(dream|visited)$")],
            ASK_NOTE:   [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_photo),
                CommandHandler("skip", skip_note),
            ],
            ASK_PHOTO:  [
                MessageHandler(filters.PHOTO, finish_with_photo),
                CommandHandler("skip", finish_no_photo),
            ],
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

    print("🌿 Her Travel Map bot is running…")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
