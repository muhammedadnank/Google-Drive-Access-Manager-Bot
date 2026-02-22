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
shutdown_requested = False

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



def _shutdown_event_loop(loop: asyncio.AbstractEventLoop):
    """Cancel pending tasks before closing loop to avoid asyncio warnings."""
    pending = [t for t in asyncio.all_tasks(loop) if not t.done()]
    for task in pending:
        task.cancel()
    if pending:
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
    loop.run_until_complete(loop.shutdown_asyncgens())

def handle_shutdown_signal(signum, _frame):
    global shutdown_requested
    shutdown_requested = True
    bot_status["running"] = False
    LOGGER.info(f"Stop signal received ({signal.Signals(signum).name}). Preparing graceful shutdown...")


if __name__ == "__main__":
    LOGGER.info("🌐 Starting Flask web server...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    LOGGER.info("🤖 Starting Telegram bot...")
    signal.signal(signal.SIGTERM, handle_shutdown_signal)
    signal.signal(signal.SIGINT, handle_shutdown_signal)

    # Import main only once
    from bot import main

    while not shutdown_requested:
        loop = None
        try:
            bot_status["running"] = True
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(main())
        except Exception as e:
            bot_status["running"] = False
            if shutdown_requested:
                LOGGER.info(f"Shutdown requested. Stopping.")
                break
            LOGGER.error(f"❌ Bot crashed: {e}. Restarting in 5 seconds...")
            time.sleep(5)
        else:
            # main() returned cleanly (stop_event fired due to SIGTERM/SIGINT)
            bot_status["running"] = False
            if shutdown_requested:
                LOGGER.info("✅ Bot exited cleanly after shutdown request. Goodbye.")
                break
            # SIGTERM came from Render infra (routine signal, not our shutdown)
            # always restart so the bot stays alive.
            LOGGER.warning("⚠️ Bot stopped (platform SIGTERM). Restarting in 5 seconds...")
            time.sleep(5)
        finally:
            if loop is not None:
                try:
                    _shutdown_event_loop(loop)
                except Exception as loop_err:
                    LOGGER.warning(f"Event loop shutdown warning: {loop_err}")
                finally:
                    try:
                        loop.close()
                    except Exception:
                        pass
