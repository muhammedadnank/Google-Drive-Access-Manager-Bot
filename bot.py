from pyrogram import Client, idle
from config import API_ID, API_HASH, BOT_TOKEN, ADMIN_IDS
from services.database import db
from services.drive import drive_service
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
                expiry_date = time.strftime('%d %b %Y %H:%M', time.localtime(g['expires_at']))
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

    LOGGER.info("🚀 Starting Bot...")
    await app.start()
    
    me = await app.get_me()
    LOGGER.info(f"✅ Bot started as @{me.username} (ID: {me.id})")
    
    # Start background expiry checker
    asyncio.create_task(expiry_checker())
    LOGGER.info("⏰ Expiry checker started (every 5 minutes)")
    
    # Start expiry notification alerts
    asyncio.create_task(expiry_notifier())
    LOGGER.info("🔔 Expiry notifier started (every 1 hour)")
    
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
    