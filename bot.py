from pyrogram import Client, idle
import pyrogram
from config import API_ID, API_HASH, BOT_TOKEN, ADMIN_IDS, VERSION
from services.database import db
from services.drive import drive_service
from utils.time import format_timestamp
import time
import asyncio
import logging

# Set start time
START_TIME = time.time()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)

# Initialize Bot
app = Client(
    "drive_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")
)


async def expiry_checker():
    """Background task to auto-revoke expired grants every 5 minutes."""
    while True:
        try:
            await asyncio.sleep(300)  # 5 minutes
            expired = await db.get_expired_grants()
            
            for grant in expired:
                try:
                    success = await drive_service.remove_access(grant["folder_id"], grant["email"])
                    if success:
                        await db.mark_grant_expired(grant["_id"])
                        await db.log_action(
                            admin_id=0,
                            admin_name="Auto-Expire",
                            action="auto_revoke",
                            details={
                                "email": grant["email"],
                                "folder_name": grant["folder_name"],
                                "folder_id": grant["folder_id"]
                            }
                        )
                        LOGGER.info(f"⏰ Auto-revoked: {grant['email']} from {grant['folder_name']}")
                    else:
                        LOGGER.warning(f"❌ Failed to auto-revoke: {grant['email']}")
                except Exception as e:
                    LOGGER.error(f"Error revoking {grant['email']}: {e}")
            
            if expired:
                LOGGER.info(f"⏰ Expiry check: {len(expired)} grant(s) processed")
        except Exception as e:
            LOGGER.error(f"Expiry checker error: {e}")


from services.broadcast import broadcast, send_daily_summary, verify_channel_access

async def daily_summary_scheduler():
    """Send daily summary every 24 hours."""
    while True:
        # Calculate time until next run (e.g., 09:00 AM local or just next 24h from start)
        # For simplicity, let's just run it every 24 hours from bot start, 
        # or better, check every minute if it's a specific time.
        # Let's keep it simple: Sleep 24h (86400s)
        await asyncio.sleep(86400)
        try:
            await send_daily_summary(app)
            LOGGER.info("📊 Daily summary sent")
        except Exception as e:
            LOGGER.error(f"Daily summary error: {e}")

async def expiry_checker():
    """Background task to auto-revoke expired grants every 5 minutes."""
    while True:
        try:
            await asyncio.sleep(300)  # 5 minutes
            expired = await db.get_expired_grants()
            
            for grant in expired:
                try:
                    success = await drive_service.remove_access(grant["folder_id"], grant["email"])
                    if success:
                        await db.mark_grant_expired(grant["_id"])
                        await db.log_action(
                            admin_id=0,
                            admin_name="Auto-Expire",
                            action="auto_revoke",
                            details={
                                "email": grant["email"],
                                "folder_name": grant["folder_name"],
                                "folder_id": grant["folder_id"]
                            }
                        )
                        # Broadcast
                        await broadcast(app, "revoke", {
                            "email": grant["email"],
                            "folder_name": grant["folder_name"],
                            "admin_name": "Auto-Expire"
                        })
                        LOGGER.info(f"⏰ Auto-revoked: {grant['email']} from {grant['folder_name']}")
                    else:
                        LOGGER.warning(f"❌ Failed to auto-revoke: {grant['email']}")
                        # Alert
                        await broadcast(app, "alert", {
                            "message": f"Failed to auto-revoke `{grant['email']}` from `{grant['folder_name']}`."
                        })
                except Exception as e:
                    LOGGER.error(f"Error revoking {grant['email']}: {e}")
                    await broadcast(app, "alert", {
                        "message": f"Error revoking `{grant['email']}`: {str(e)}"
                    })
            
            if expired:
                LOGGER.info(f"⏰ Expiry check: {len(expired)} grant(s) processed")
        except Exception as e:
            LOGGER.error(f"Expiry checker error: {e}")


async def expiry_notifier():
    """Background task to notify admins about grants expiring within 24 hours."""
    notified_grants = set()  # Track already-notified grant IDs
    
    while True:
        try:
            await asyncio.sleep(3600)  # Check every hour
            
            grants = await db.get_active_grants()
            now = time.time()
            
            expiring_soon = [
                g for g in grants 
                if 0 < g.get('expires_at', 0) - now < 86400
                and str(g.get('_id')) not in notified_grants
            ]
            
            if not expiring_soon:
                continue
            
            # Build notification message
            text = f"⚠️ **Expiry Alert** — {len(expiring_soon)} grant(s) expiring within 24h:\n\n"
            
            for g in expiring_soon[:10]:
                remaining_hrs = int((g['expires_at'] - now) / 3600)
                expiry_date = format_timestamp(g['expires_at'])
                text += (
                    f"📧 `{g['email']}`\n"
                    f"   📂 {g['folder_name']} | ⏳ ~{remaining_hrs}h left\n"
                    f"   📅 Expires: {expiry_date}\n\n"
                )
                notified_grants.add(str(g['_id']))
            
            if len(expiring_soon) > 10:
                text += f"... +{len(expiring_soon) - 10} more\n\n"
            
            text += "Use /start → ⏰ Expiry Dashboard to manage."
            
            # Send to all admins
            for admin_id in ADMIN_IDS:
                try:
                    await app.send_message(admin_id, text)
                except Exception as e:
                    LOGGER.warning(f"Could not notify admin {admin_id}: {e}")
            
            LOGGER.info(f"⚠️ Expiry notification sent for {len(expiring_soon)} grants")
            
            # Clean up old entries to prevent memory leak
            if len(notified_grants) > 1000:
                notified_grants.clear()
                
        except Exception as e:
            LOGGER.error(f"Expiry notifier error: {e}")


async def main():
    # Connect to MongoDB
    await db.init()
    
    # Authenticate Drive Service
    if drive_service.authenticate():
        LOGGER.info("✅ Google Drive Service authenticated!")
    else:
        LOGGER.warning("⚠️ Could not authenticate Google Drive Service. Check credentials.json.")
        await broadcast(app, "alert", {"message": "⚠️ Google Drive Service authentication failed!"})

    LOGGER.info("🚀 Starting Bot...")
    await app.start()
    
    me = await app.get_me()
    LOGGER.info(f"✅ Bot started as @{me.username} (ID: {me.id})")
    
    # Verify Channel Access
    await verify_channel_access(app)
    
    # Broadcast Startup
    try:
        await broadcast(app, "bot_start", {
            "bot_name": me.first_name,
            "bot_id": me.id,
            "pyro_version": pyrogram.__version__,
            "version": VERSION
        })
        LOGGER.info("📢 Startup notification sent to channel")
    except Exception as e:
        LOGGER.error(f"Startup broadcast failed: {e}")
    
    # Start background expiry checker
    asyncio.create_task(expiry_checker())
    LOGGER.info("⏰ Expiry checker started (every 5 minutes)")
    
    # Start expiry notification alerts
    asyncio.create_task(expiry_notifier())
    LOGGER.info("🔔 Expiry notifier started (every 1 hour)")
    
    # Start daily summary
    asyncio.create_task(daily_summary_scheduler())
    LOGGER.info("📊 Daily summary scheduler started (every 24 hours)")
    
    # Keep the bot running
    await idle()
    
    await app.stop()

if __name__ == "__main__":
    if not API_ID or not API_HASH:
        LOGGER.error("❌ API_ID and API_HASH are required in .env")
        exit(1)
    if not BOT_TOKEN:
        LOGGER.error("❌ BOT_TOKEN is required in .env")
        exit(1)
        
    app.run(main())
    