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

if __name__ == "__main__":
    # Start Flask daemon thread first
    LOGGER.info("🌐 Starting Flask web server...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    LOGGER.info("🤖 Starting Telegram bot...")

    # Ignore SIGTERM so Render doesn't kill the process on idle
    signal.signal(signal.SIGTERM, signal.SIG_IGN)

    from bot import main

    while True:
        try:
            bot_status["running"] = True
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(main())
        except Exception as e:
            LOGGER.error(f"❌ Bot crashed: {e}. Restarting in 5 seconds...")
            bot_status["running"] = False
            time.sleep(5)
        else:
            LOGGER.info("Bot exited cleanly. Restarting in 5 seconds...")
            bot_status["running"] = False
            time.sleep(5)
        finally:
            try:
                loop.close()
            except Exception:
                pass
