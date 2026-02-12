from pyrogram import Client, filters
from services.database import db
from config import ADMIN_IDS
import time
import sys
import pyrogram
import logging

LOGGER = logging.getLogger(__name__)

# Bot start time — set on import
BOT_START_TIME = time.time()


def _is_super_admin(user_id):
    """Only the first admin in ADMIN_IDS is super admin."""
    return ADMIN_IDS and int(user_id) == int(ADMIN_IDS[0])


@Client.on_message(filters.command("info"))
async def info_command(client, message):
    """System monitoring — super admin only."""
    if not _is_super_admin(message.from_user.id):
        await message.reply_text("🔒 This command is restricted to super admins.")
        return
    
    msg = await message.reply_text("🔧 Loading system info...")
    
    try:
        # Uptime
        uptime_secs = int(time.time() - BOT_START_TIME)
        days = uptime_secs // 86400
        hours = (uptime_secs % 86400) // 3600
        minutes = (uptime_secs % 3600) // 60
        uptime_text = f"{days}d {hours}h {minutes}m" if days else f"{hours}h {minutes}m"
        
        # DB health
        try:
            await db.db.command("ping")
            db_status = "✅ Connected"
        except Exception:
            db_status = "❌ Disconnected"
        
        # Collection counts
        logs_count = await db.logs.count_documents({"is_deleted": {"$ne": True}})
        grants_active = await db.grants.count_documents({"status": "active"})
        grants_total = await db.grants.count_documents({})
        templates_count = await db.templates.count_documents({})
        admins_count = await db.admins.count_documents({})
        
        text = (
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔧 **System Monitor**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            "🤖 **Bot Status**\n"
            f"┣ Uptime: `{uptime_text}`\n"
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
        
        await msg.edit_text(text)
        
    except Exception as e:
        LOGGER.error(f"Info command error: {e}")
        await msg.edit_text(f"❌ Error: {e}")
