"""
Web server for Render deployment.
Flask runs in a daemon thread, bot runs in the main thread.
"""
import os
import sys
import threading
import logging
from flask import Flask, jsonify, request

# Ensure project directory is in sys.path for plugin imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

LOGGER = logging.getLogger(__name__)

# Import bot components
from bot import app as bot_app, main

# Flask app for health checks
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

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Start Flask in a daemon thread (for Render health checks)
    LOGGER.info("🌐 Starting Flask web server...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Run bot in the MAIN thread (required for proper asyncio handling)
    LOGGER.info("🤖 Starting Telegram bot in main thread...")
    bot_status["running"] = True
    import asyncio
    asyncio.run(main())
