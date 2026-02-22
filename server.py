"""
Web server for Render deployment.
Flask runs in a daemon thread, bot runs in the main thread with a single event loop.
"""
import os
import sys
import threading
import logging
import asyncio
from flask import Flask, jsonify

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

LOGGER = logging.getLogger(__name__)

from bot import app as bot_app, main

flask_app = Flask(__name__)

bot_status = {
    "running": False,
    "bot_info": None
}

@flask_app.route("/")
@flask_app.route("/status")
def status():
    return jsonify({
        "status": "running" if bot_status["running"] else "starting",
        "bot": bot_status.get("bot_info", "loading...")
    })

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
    """Run Flask in a daemon thread for health checks."""
    port = int(os.getenv("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port, use_reloader=False)

async def run_all():
    """Run Flask in a thread and bot in the same event loop."""
    # Start Flask daemon thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    LOGGER.info("🌐 Flask web server started")

    # Run bot in this event loop
    LOGGER.info("🤖 Starting Telegram bot...")
    bot_status["running"] = True
    await main()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    asyncio.run(run_all())
