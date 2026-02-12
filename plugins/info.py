from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.database import db
from config import ADMIN_IDS, START_TIME
import time
import sys
import pyrogram
import logging
from utils.time import get_uptime

LOGGER = logging.getLogger(__name__)

def _is_super_admin(user_id):
    """Only the first admin in ADMIN_IDS is super admin."""
    return ADMIN_IDS and int(user_id) == int(list(ADMIN_IDS)[0])


async def _get_info_text():
    uptime = get_uptime(START_TIME)
    
    # DB Stats
    try:
        await db.db.command("ping")
        db_status = "✅ Connected"
    except Exception:
        db_status = "❌ Disconnected"
        
    logs_count = await db.logs.count_documents({"is_deleted": {"$ne": True}})
    grants_active = await db.grants.count_documents({"status": "active"})
    grants_total = await db.grants.count_documents({})
    templates_count = await db.templates.count_documents({})
    admins_count = await db.admins.count_documents({})
    
    status_text = (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔧 **System Monitor**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🤖 **Bot Status**\n"
        f"┣ Uptime: `{uptime}`\n"
        f"┣ Python: `{sys.version.split()[0]}`\n"
        f"┗ Pyrogram: `{pyrogram.__version__}`\n\n"
        "🗄 **Database**\n"
        f"┣ Status: {db_status}\n"
        f"┣ Admins: `{admins_count}`\n"
        f"┣ Logs: `{logs_count}`\n"
        f"┣ Grants (active): `{grants_active}`\n"
        f"┣ Grants (total): `{grants_total}`\n"
        f"┗ Templates: `{templates_count}`\n\n"
        "⏰ **Scheduler**\n"
        "┗ Auto-expire: runs every 5 min"
    )
    return status_text

@Client.on_message(filters.command("info"))
async def info_command(client, message):
    user_id = message.from_user.id
    if not _is_super_admin(user_id):
        return
        
    msg = await message.reply_text("🔧 Loading...")
    try:
        text = await _get_info_text()
        await msg.edit_text(text)
    except Exception as e:
        LOGGER.error(f"Info error: {e}")
        await msg.edit_text(f"❌ Error: {e}")

@Client.on_callback_query(filters.regex("^info_callback$"))
async def info_callback(client, callback_query):
    user_id = callback_query.from_user.id
    if not _is_super_admin(user_id):
        await callback_query.answer("🔒 Super Admin only!", show_alert=True)
        return
        
    try:
        text = await _get_info_text()
        await callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ])
        )
    except Exception as e:
        LOGGER.error(f"Info callback error: {e}")
        await callback_query.answer("❌ Error loading info", show_alert=True)
