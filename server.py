"""
Flask web server for Render deployment.
Provides health check endpoint and runs the bot in a separate thread.
"""

from flask import Flask, jsonify
from threading import Thread
import logging
import asyncio
from bot import app, main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)

# Create Flask app
flask_app = Flask(__name__)

# Bot status
bot_status = {
    "running": False,
    "username": None,
    "bot_id": None
}

def run_bot():
    """Run the Telegram bot in a separate thread."""
    try:
        LOGGER.info("🤖 Starting Telegram bot...")
        bot_status["running"] = True
        asyncio.run(main())
    except Exception as e:
        LOGGER.error(f"❌ Bot error: {e}")
        bot_status["running"] = False

@flask_app.route('/')
def home():
    """Home endpoint - health check."""
    return jsonify({
        "status": "online",
        "service": "Google Drive Access Manager Bot",
        "bot_running": bot_status["running"],
        "bot_username": bot_status.get("username"),
        "bot_id": bot_status.get("bot_id")
    })

@flask_app.route('/health')
def health():
    """Health check endpoint for Render."""
    if bot_status["running"]:
        return jsonify({"status": "healthy", "bot": "running"}), 200
    else:
        return jsonify({"status": "unhealthy", "bot": "stopped"}), 503

@flask_app.route('/status')
def status():
    """Detailed status endpoint."""
    return jsonify({
        "bot_status": bot_status,
        "server": "running"
    })

if __name__ == "__main__":
    # Start bot in a separate thread
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    LOGGER.info("🌐 Starting Flask web server...")
    
    # Get port from environment (Render provides PORT env var)
    import os
    port = int(os.getenv("PORT", 5000))
    
    # Run Flask app
    flask_app.run(host="0.0.0.0", port=port, debug=False)
