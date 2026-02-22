"""
Web server for Render deployment.
Flask runs in a daemon thread.
Bot runs as a SUBPROCESS so that Render's SIGTERM is caught here,
not by Pyrogram/Kurigram's idle() — which would kill the bot permanently.
"""
import os
import sys
import subprocess
import threading
import logging
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
bot_process = None  # current subprocess


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


def handle_shutdown_signal(signum, _frame):
    """Called when Render sends SIGTERM/SIGINT to THIS process."""
    global shutdown_requested, bot_process
    shutdown_requested = True
    bot_status["running"] = False
    sig_name = signal.Signals(signum).name
    LOGGER.info(f"Stop signal ({sig_name}) received by server. Shutting down...")
    if bot_process and bot_process.poll() is None:
        LOGGER.info("Terminating bot subprocess...")
        bot_process.terminate()
        try:
            bot_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            bot_process.kill()


def run_bot_subprocess():
    """
    Run bot.py as a child subprocess in a loop.
    If the bot exits for ANY reason (including SIGTERM sent directly to it
    by the platform), restart it unless WE requested shutdown.
    """
    global bot_process, shutdown_requested

    python = sys.executable

    while not shutdown_requested:
        LOGGER.info("Starting bot subprocess...")
        bot_process = subprocess.Popen(
            [python, "bot.py"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        bot_status["running"] = True
        LOGGER.info(f"Bot subprocess started (PID={bot_process.pid})")

        bot_process.wait()
        bot_status["running"] = False
        exit_code = bot_process.returncode
        LOGGER.info(f"Bot subprocess exited with code {exit_code}")

        if shutdown_requested:
            LOGGER.info("Shutdown requested. Not restarting bot.")
            break

        LOGGER.warning(f"Bot exited (code={exit_code}). Restarting in 5 seconds...")
        time.sleep(5)

    LOGGER.info("Bot runner loop finished.")


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_shutdown_signal)
    signal.signal(signal.SIGINT, handle_shutdown_signal)

    LOGGER.info("Starting Flask web server thread...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    LOGGER.info("Starting bot runner thread...")
    bot_thread = threading.Thread(target=run_bot_subprocess, daemon=False)
    bot_thread.start()

    bot_thread.join()
    LOGGER.info("server.py exiting.")
