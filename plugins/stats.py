from pyrogram import Client, filters
from services.database import db
from utils.filters import is_admin
import logging

LOGGER = logging.getLogger(__name__)


@Client.on_message(filters.command("stats") & is_admin)
async def stats_command(client, message):
    """Activity analytics dashboard."""
    msg = await message.reply_text("📊 Loading stats...")
    
    try:
        stats = await db.get_stats()
    except Exception as e:
        LOGGER.error(f"Stats error: {e}")
        await msg.edit_text("❌ Failed to load stats.")
        return
    
    # IMPROVED: Add expiring soon count
    import time
    active_grants_list = await db.get_active_grants()
    now = time.time()
    expiring_24h = sum(1 for g in active_grants_list if 0 < g.get("expires_at", 0) - now < 86400)

    text = (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 **Activity Dashboard**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"

        "📅 **Activity Count**\n"
        f"┣ Today: **{stats['today']}**\n"
        f"┣ This Week: **{stats['week']}**\n"
        f"┣ This Month: **{stats['month']}**\n"
        f"┗ All Time: **{stats['total']}**\n\n"

        "📂 **Top Folder (This Month)**\n"
        f"┗ {stats['top_folder']} ({stats['top_folder_count']} actions)\n\n"

        "👤 **Top Admin (This Month)**\n"
        f"┗ {stats['top_admin']} ({stats['top_admin_count']} actions)\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📈 **System Counts**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"┣ ⏰ Active Timed Grants: **{stats['active_grants']}**\n"
        f"┗ ⚠️ Expiring in 24h: **{expiring_24h}**"
    )
    
    await msg.edit_text(text)