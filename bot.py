from pyrogram import Client, idle
from config import API_ID, API_HASH, BOT_TOKEN
from services.database import db
from services.drive import drive_service
import asyncio
import logging
import traceback

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
