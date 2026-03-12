import logging
import datetime

from pyrogram import Client, filters
from pyrogram.enums import ButtonStyle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from services.database import db
from utils.filters import is_admin
from utils.time import safe_edit, IST

LOGGER = logging.getLogger(__name__)

TYPE_ICONS = {
    "grant":       "➕",
    "role_change": "🔄",
    "remove":      "🗑",
    "revoke":      "🗑",
    "auto_revoke": "▪️",
    "bulk_revoke": "🗑",
    "bulk_import": "📥",
    "extend":      "🔄",
}

# /logs COMMAND  +  logs_menu CALLBACK

@Client.on_message(filters.command("logs") & filters.private & is_admin)
async def logs_command(client, message):
    """Entry point via /logs command."""
    logs, total = await db.get_logs(limit=50)

    if not logs:
        await message.reply_text(
            "📊 **Access Logs**\n\nNo activity recorded yet.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Back", callback_data="main_menu", style=ButtonStyle.PRIMARY)
            ]])
        )
        return

    await db.set_state(message.from_user.id, "VIEWING_LOGS", {"logs": logs})
    msg = await message.reply_text("📊 Loading logs...")
    await _show_logs_page(msg, logs, 1, is_message=True)


@Client.on_callback_query(filters.regex("^logs_menu$") & is_admin)
async def view_logs(client, callback_query):
    """Entry point via inline button."""
    logs, total = await db.get_logs(limit=50)

    if not logs:
        await safe_edit(callback_query,
            "📊 **Access Logs**\n\nNo activity recorded yet.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Back", callback_data="main_menu", style=ButtonStyle.PRIMARY)
            ]])
        )
        return

    await db.set_state(callback_query.from_user.id, "VIEWING_LOGS", {"logs": logs})
    await _show_logs_page(callback_query, logs, 1)

# Shared Page Renderer

async def _show_logs_page(target, logs, page, is_message=False):
    per_page    = 5
    start       = (page - 1) * per_page
    total_pages = (len(logs) + per_page - 1) // per_page
    current     = logs[start:start + per_page]

    text = f"📊 **Activity Logs (Page {page}/{total_pages})**\n\n"

    for log in current:
        ts       = datetime.datetime.fromtimestamp(log["timestamp"], tz=IST).strftime("%d %b %Y, %I:%M %p")
        log_type = log.get("type", log.get("action", "unknown"))
        icon     = TYPE_ICONS.get(log_type, "▪️")
        action   = log_type.replace("_", " ").upper()
        details  = log.get("details", {})
        email    = details.get("email", "N/A")
        folder   = details.get("folder_name", details.get("folder", "Unknown"))

        text += f"{icon} `{action}` → `{email}`\n"
        text += f"   📂 {folder} 🕒 {ts}\n\n"

    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"log_page_{page - 1}", style=ButtonStyle.PRIMARY))
    if page < total_pages:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"log_page_{page + 1}", style=ButtonStyle.PRIMARY))

    keyboard = [nav] if nav else []
    keyboard.append([InlineKeyboardButton("📤 Export as CSV", callback_data="export_logs",  style=ButtonStyle.SUCCESS)])
    keyboard.append([InlineKeyboardButton("🗑 Clear Logs",    callback_data="clear_logs",   style=ButtonStyle.DANGER)])
    keyboard.append([InlineKeyboardButton("🏠 Back",          callback_data="main_menu",    style=ButtonStyle.PRIMARY)])

    markup = InlineKeyboardMarkup(keyboard)
    if is_message:
        try:
            await target.edit_text(text, reply_markup=markup)
        except Exception as e:
            LOGGER.debug(f"Logs page edit: {e}")
    else:
        await safe_edit(target, text, reply_markup=markup)

# Pagination & Actions

@Client.on_callback_query(filters.regex(r"^log_page_(\d+)$") & is_admin)
async def logs_pagination(client, callback_query):
    page = int(callback_query.matches[0].group(1))
    user_id = callback_query.from_user.id
    state, data = await db.get_state(user_id)

    if state != "VIEWING_LOGS":
        return

    await _show_logs_page(callback_query, data["logs"], page)


@Client.on_callback_query(filters.regex("^clear_logs$") & is_admin)
async def clear_logs_handler(client, callback_query):
    await db.clear_logs()
    await callback_query.answer("Logs cleared!")
    await safe_edit(callback_query,
        "🗑 **Logs Cleared**\n\nAll activity logs have been removed.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🏠 Back", callback_data="main_menu", style=ButtonStyle.PRIMARY)
        ]])
    )
