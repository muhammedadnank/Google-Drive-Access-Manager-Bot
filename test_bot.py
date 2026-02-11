"""
Simple test bot to debug message reception.
Run this directly: python test_bot.py
"""
from pyrogram import Client, filters, ContinuePropagation
from config import API_ID, API_HASH, BOT_TOKEN
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)

app = Client(
    "test_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# Raw update handler in group -1 (runs first, then propagates)
@app.on_raw_update(group=-1)
async def raw_handler(client, update, users, chats):
    LOGGER.info(f"📩 RAW UPDATE: {type(update).__name__}")
    raise ContinuePropagation

# Catch ALL messages - no filters at all
@app.on_message(group=0)
async def catch_all(client, message):
    LOGGER.info(f"📨 MESSAGE from {message.from_user.id}: {message.text}")
    await message.reply_text(f"✅ Got your message!\nYour ID: `{message.from_user.id}`")

if __name__ == "__main__":
    LOGGER.info("🚀 Starting test bot...")
    app.run()
