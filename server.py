"""
Web server for Render deployment.
Flask runs in a daemon thread.
Bot runs with its own event loop in main thread.
"""
import os
import sys
import threading
import logging
import asyncio
import signal
import time
from flask import Flask, jsonify

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)

flask_app = Flask(__name__)

bot_status = {"running": False}

@flask_app.route("/")
@flask_app.route("/status")
def status():
    return jsonify({"status": "running" if bot_status["running"] else "starting"})

@flask_app.route("/health")
def health():
    return "OK", 200

@flask_app.route("/oauth/callback")
def oauth_callback():
    return """
    <html><body>
    <h2>✅ Authorization received!</h2>
    <p>Copy the full URL from your browser address bar and paste it in the bot.</p>
    </body></html>
    """, 200

def run_flask():
    port = int(os.getenv("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port, use_reloader=False)

async def run_bot():
    """Create a fresh bot instance and run it."""
    from config import API_ID, API_HASH, BOT_TOKEN
    from pyrogram import Client, idle
    from services.database import db
    from services.broadcast import broadcast, send_daily_summary, verify_channel_access
    from config import VERSION
    import time as _time

    START_TIME = _time.time()

    # Fresh Client every restart — avoids "attached to different loop" error
    app = Client(
        "drive_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        plugins=dict(root="plugins")
    )

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

    await app.start()
    me = await app.get_me()
    LOGGER.info(f"✅ Bot started as @{me.username} (ID: {me.id})")

    await verify_channel_access(app)

    try:
        await broadcast(app, "bot_start", {
            "bot_name": me.first_name, "bot_id": me.id,
            "pyrofork_version": "2.2.19", "version": VERSION
        })
    except Exception as e:
        LOGGER.error(f"Startup broadcast failed: {e}")

    # Import bot tasks
    from bot import expiry_checker, expiry_notifier, daily_summary_scheduler
    asyncio.create_task(expiry_checker())
    LOGGER.info("⏰ Expiry checker started (every 5 min)")
    asyncio.create_task(expiry_notifier())
    LOGGER.info("🔔 Expiry notifier started (every 1 hour, with action buttons)")
    asyncio.create_task(daily_summary_scheduler())
    LOGGER.info("📊 Daily summary scheduler started")

    await idle()
    await app.stop()

if __name__ == "__main__":
    # Start Flask daemon thread first
    LOGGER.info("🌐 Starting Flask web server...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    LOGGER.info("🤖 Starting Telegram bot...")

    # Ignore SIGTERM so Render doesn't kill the process on idle
    signal.signal(signal.SIGTERM, signal.SIG_IGN)

    while True:
        try:
            bot_status["running"] = True
            # Fresh event loop + fresh Client every restart
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(run_bot())
        except Exception as e:
            LOGGER.error(f"❌ Bot crashed: {e}. Restarting in 5 seconds...")
            bot_status["running"] = False
        else:
            LOGGER.info("Bot exited cleanly. Restarting in 5 seconds...")
            bot_status["running"] = False
        finally:
            try:
                loop.close()
            except Exception:
                pass
            time.sleep(5)
