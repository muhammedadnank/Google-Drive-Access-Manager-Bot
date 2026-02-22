from pyrogram import Client, idle
import pyrogram
from config import API_ID, API_HASH, BOT_TOKEN, ADMIN_IDS, VERSION
from services.database import db
from services.drive import drive_service
from utils.time import format_timestamp
import time
import asyncio
import logging
from uuid import uuid4

START_TIME = time.time()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)

# Constants
EXPIRY_CHECK_INTERVAL = 300      # 5 minutes
NOTIFICATION_INTERVAL = 3600     # 1 hour
DAILY_SUMMARY_INTERVAL = 86400   # 24 hours
NOTIFICATION_TTL = 90000         # 25 hours
MAX_NOTIFICATIONS_PER_BATCH = 20

# Security: Helper to hash emails in logs
import hashlib

def sanitize_email(email: str) -> str:
    """Hash emails/strings for privacy logs."""
    if not email: return "N/A"
    return hashlib.sha256(str(email).encode()).hexdigest()[:8]

# app is created fresh each run via make_app() — do NOT create global Client here
# Plugins reference 'app' via the Client passed into handlers by Pyrogram, not this module's global.

from services.broadcast import broadcast, send_daily_summary, verify_channel_access


def make_app():
    """Create a fresh Client instance each time — avoids 'attached to different loop' error.
    in_memory=True avoids SQLite session file lock on restart.
    A unique in-memory session name per process prevents stale lock contention
    if the hosting platform briefly overlaps old/new processes during deploys.
    """
    return Client(
        f"drive_bot_{uuid4().hex}",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        plugins=dict(root="plugins"),
        in_memory=True
    )


async def expiry_checker(app):
    """Background task: auto-revoke expired grants every 5 minutes."""
    while True:
        try:
            await asyncio.sleep(EXPIRY_CHECK_INTERVAL)
            expired = await db.get_expired_grants()
            for grant in expired:
                try:
                    success = await drive_service.remove_access(grant["folder_id"], grant["email"], db)
                    if success:
                        await db.mark_grant_expired(grant["_id"])
                        await db.log_action(
                            admin_id=0, admin_name="Auto-Expire", action="auto_revoke",
                            details={"email": grant["email"], "folder_name": grant["folder_name"], "folder_id": grant["folder_id"]}
                        )
                        await broadcast(app, "revoke", {
                            "email": grant["email"], "folder_name": grant["folder_name"], "admin_name": "Auto-Expire"
                        })
                        LOGGER.info(f"⏰ Auto-revoked: {sanitize_email(grant['email'])} from {grant['folder_name']}")
                    else:
                        await db.mark_grant_revocation_failed(grant["_id"])
                        err_msg = f"Failed to auto-revoke `{grant['email']}` from `{grant['folder_name']}`. Status set to 'revocation_failed'. Check manually."
                        await broadcast(app, "alert", {"message": err_msg})
                        LOGGER.error(f"❌ {err_msg}")
                except Exception as e:
                    LOGGER.error(f"Error revoking {sanitize_email(grant['email'])}: {e}")
                    await broadcast(app, "alert", {"message": f"Error revoking `{grant['email']}`: {str(e)}"})
            if expired:
                LOGGER.info(f"⏰ Expiry check: {len(expired)} grant(s) processed")
        except Exception as e:
            LOGGER.error(f"Expiry checker error: {e}")


async def expiry_notifier(app):
    """
    IMPROVED: Notify admins of expiring grants with inline action buttons.
    TTL-based cleanup prevents memory leak.
    """
    notified_grants = {}  # grant_id -> notified_at timestamp

    while True:
        try:
            await asyncio.sleep(NOTIFICATION_INTERVAL)
            grants = await db.get_active_grants()
            now = time.time()

            # TTL cleanup: remove entries older than 25 hours
            notified_grants = {gid: ts for gid, ts in notified_grants.items() if now - ts < NOTIFICATION_TTL}

            expiring_soon = [
                g for g in grants
                if 0 < g.get('expires_at', 0) - now < 86400
                and str(g.get('_id')) not in notified_grants
            ]

            if not expiring_soon:
                continue

            from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

            for g in expiring_soon[:MAX_NOTIFICATIONS_PER_BATCH]:
                remaining_hrs = max(1, int((g['expires_at'] - now) / 3600))
                expiry_date = format_timestamp(g['expires_at'])
                grant_id_short = str(g['_id'])[:20]

                text = (
                    f"⚠️ **Expiry Alert**\n\n"
                    f"📧 `{g['email']}`\n"
                    f"📂 {g['folder_name']}\n"
                    f"🔑 {g.get('role', 'viewer').capitalize()}\n"
                    f"⏳ ~{remaining_hrs}h remaining\n"
                    f"📅 Expires: {expiry_date}\n\n"
                    f"Take action:"
                )
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("🔄 Extend +7 Days", callback_data=f"notif_ext_168_{grant_id_short}"),
                        InlineKeyboardButton("🗑 Revoke Now", callback_data=f"notif_rev_{grant_id_short}"),
                    ],
                    [InlineKeyboardButton("⏭ Ignore", callback_data="noop")]
                ])

                for admin_id in ADMIN_IDS:
                    try:
                        await app.send_message(admin_id, text, reply_markup=keyboard)
                    except Exception as e:
                        LOGGER.warning(f"Could not notify admin {admin_id}: {e}")

                notified_grants[str(g['_id'])] = now

            LOGGER.info(f"⚠️ Expiry notification sent for {len(expiring_soon)} grants")

        except Exception as e:
            LOGGER.error(f"Expiry notifier error: {e}")


async def daily_summary_scheduler(app):
    """Send daily summary every 24 hours."""
    while True:
        await asyncio.sleep(DAILY_SUMMARY_INTERVAL)
        try:
            await send_daily_summary(app)
            LOGGER.info("📊 Daily summary sent")
        except Exception as e:
            LOGGER.error(f"Daily summary error: {e}")


async def main():
    await db.init()

    try:
        channel_config = await db.get_setting("channel_config")
        if channel_config:
            LOGGER.info(f"✅ Channel config loaded: ID={channel_config.get('channel_id')}")
        else:
            LOGGER.info("⚠️ No channel config found - using defaults")
    except Exception as e:
        LOGGER.error(f"❌ Failed to load channel config: {e}")

    LOGGER.info("ℹ️ Google Drive: Use /auth in bot to connect your Google account.")
    LOGGER.info("🚀 Starting Bot...")

    # Fresh Client every call — no global Client object
    app = make_app()
    await app.start()

    me = await app.get_me()
    LOGGER.info(f"✅ Bot started as @{me.username} (ID: {me.id})")

    await verify_channel_access(app)

    try:
        await broadcast(app, "bot_start", {
            "bot_name": me.first_name, "bot_id": me.id,
            "pyrofork_version": pyrogram.__version__, "version": VERSION
        })
    except Exception as e:
        LOGGER.error(f"Startup broadcast failed: {e}")

    asyncio.create_task(expiry_checker(app))
    LOGGER.info("⏰ Expiry checker started (every 5 min)")

    asyncio.create_task(expiry_notifier(app))
    LOGGER.info("🔔 Expiry notifier started (every 1 hour, with action buttons)")

    asyncio.create_task(daily_summary_scheduler(app))
    LOGGER.info("📊 Daily summary scheduler started")

    await idle()
    await app.stop()


if __name__ == "__main__":
    if not API_ID or not API_HASH:
        LOGGER.error("❌ API_ID and API_HASH are required in .env")
        exit(1)
    if not BOT_TOKEN:
        LOGGER.error("❌ BOT_TOKEN is required in .env")
        exit(1)
    import asyncio as _asyncio
    _asyncio.run(main())
