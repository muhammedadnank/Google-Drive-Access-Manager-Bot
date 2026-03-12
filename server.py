"""
server.py — Web server for Render/Railway deployment.

Flask runs in a daemon thread.
Bot runs as a SUBPROCESS — stdout/stderr piped so all logs are visible.
SIGTERM from Render is caught and forwarded to the bot process.

Upgrades over previous version:
  - /health    → real bot-process liveness check (not always OK)
  - /status    → uptime + restart count + PID + version JSON
  - /metrics   → active grants count from MongoDB (lightweight)
  - /oauth/callback → improved HTML with auto-select URL
  - Exponential backoff on restart (5 → 10 → 20 → 40 → max 60s)
  - threading.Event for thread-safe bot_running state
  - stream_output label actually used in log prefix
  - Startup banner with Python version + platform info
"""

import os
import sys
import platform
import subprocess
import threading
import logging
import signal
import time

from flask import Flask, jsonify

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Logging ───────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
LOGGER = logging.getLogger(__name__)

# ── Flask app ─────────────────────────────────────────────────
flask_app = Flask(__name__)

# ── Shared state (thread-safe) ────────────────────────────────
_bot_running   = threading.Event()   # set = running, clear = stopped
_shutdown      = threading.Event()   # set = shutdown requested

_state = {
    "start_time":     time.time(),
    "restart_count":  0,
    "bot_pid":        None,
    "last_exit_code": None,
}

bot_process: subprocess.Popen | None = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Flask Routes
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@flask_app.route("/")
@flask_app.route("/status")
def status():
    """
    Returns JSON with runtime info.
    Used by UptimeRobot / monitoring dashboards.
    """
    uptime_secs = int(time.time() - _state["start_time"])
    days, rem   = divmod(uptime_secs, 86400)
    hours, rem  = divmod(rem, 3600)
    mins        = rem // 60

    uptime_str = ""
    if days:  uptime_str += f"{days}d "
    if hours: uptime_str += f"{hours}h "
    uptime_str += f"{mins}m"

    # Try to read version from config without importing the full stack
    try:
        import config
        version = getattr(config, "VERSION", "unknown")
    except Exception:
        version = "unknown"

    return jsonify({
        "status":        "running" if _bot_running.is_set() else "starting",
        "uptime":        uptime_str.strip(),
        "uptime_secs":   uptime_secs,
        "restart_count": _state["restart_count"],
        "bot_pid":       _state["bot_pid"],
        "last_exit_code": _state["last_exit_code"],
        "version":       version,
        "python":        platform.python_version(),
    })


@flask_app.route("/health")
def health():
    """
    Real liveness check — returns 200 only if bot subprocess is alive.
    Render uses this to decide whether to restart the service.
    Previously always returned 200 even when bot was dead.
    """
    if bot_process is not None and bot_process.poll() is None:
        return "OK", 200
    # Bot not running — return 503 so Render/UptimeRobot knows
    return "Bot not running", 503


@flask_app.route("/metrics")
def metrics():
    """
    Lightweight operational metrics.
    Queries MongoDB for active grant count — useful for monitoring dashboards.
    Fails gracefully if DB is unreachable.
    """
    try:
        import asyncio
        from services.database import db

        loop = asyncio.new_event_loop()
        grants = loop.run_until_complete(db.get_active_grants())
        loop.close()

        now = time.time()
        expiring_soon = sum(
            1 for g in grants
            if 0 < g.get("expires_at", 0) - now < 86400
        )
        return jsonify({
            "active_grants":   len(grants),
            "expiring_soon":   expiring_soon,
            "bot_running":     _bot_running.is_set(),
            "restart_count":   _state["restart_count"],
        })
    except Exception as e:
        return jsonify({"error": str(e), "bot_running": _bot_running.is_set()}), 500


@flask_app.route("/oauth/callback")
def oauth_callback():
    """
    OAuth redirect landing page.
    Improved: shows the full URL clearly with an auto-select button.
    """
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Google Drive Bot — OAuth</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #0f0f0f; color: #e0e0e0;
      min-height: 100vh; display: flex;
      align-items: center; justify-content: center; padding: 20px;
    }
    .card {
      background: #1a1a2e; border: 1px solid #2d2d4e;
      border-radius: 16px; padding: 36px 32px;
      max-width: 540px; width: 100%; text-align: center;
    }
    .icon { font-size: 48px; margin-bottom: 16px; }
    h1 { font-size: 22px; color: #4ade80; margin-bottom: 8px; }
    p  { color: #9ca3af; font-size: 14px; line-height: 1.6; margin-bottom: 20px; }
    .url-box {
      background: #0d0d1a; border: 1px solid #3b3b6b;
      border-radius: 10px; padding: 12px 16px;
      font-family: monospace; font-size: 12px;
      color: #a78bfa; word-break: break-all;
      text-align: left; margin-bottom: 16px;
      max-height: 80px; overflow-y: auto;
    }
    button {
      background: #4f46e5; color: white;
      border: none; border-radius: 10px;
      padding: 12px 28px; font-size: 15px;
      cursor: pointer; width: 100%;
      transition: background 0.2s;
    }
    button:hover { background: #4338ca; }
    button:active { background: #3730a3; }
    .copied { background: #16a34a !important; }
    .step {
      background: #111827; border-radius: 10px;
      padding: 16px; text-align: left;
      margin-bottom: 20px;
    }
    .step li { margin: 6px 0; font-size: 13px; color: #d1d5db; }
    .step li span { color: #60a5fa; font-weight: 600; }
  </style>
</head>
<body>
  <div class="card">
    <div class="icon">✅</div>
    <h1>Authorization Received!</h1>
    <p>Google has redirected you here. Now send this URL back to your bot.</p>

    <div class="url-box" id="urlBox"></div>

    <button id="copyBtn" onclick="copyUrl()">📋 Copy Full URL</button>

    <br><br>
    <div class="step">
      <ol>
        <li><span>Step 1:</span> Click "Copy Full URL" above</li>
        <li><span>Step 2:</span> Go back to Telegram</li>
        <li><span>Step 3:</span> Paste the URL and send it to the bot</li>
        <li><span>Step 4:</span> Done! ✅</li>
      </ol>
    </div>

    <p style="font-size:12px; color:#6b7280;">
      This page is safe to close after copying the URL.
    </p>
  </div>

  <script>
    const url = window.location.href;
    document.getElementById("urlBox").textContent = url;

    function copyUrl() {
      navigator.clipboard.writeText(url).then(() => {
        const btn = document.getElementById("copyBtn");
        btn.textContent = "✅ Copied!";
        btn.classList.add("copied");
        setTimeout(() => {
          btn.textContent = "📋 Copy Full URL";
          btn.classList.remove("copied");
        }, 2500);
      }).catch(() => {
        // Fallback: select the text
        const box = document.getElementById("urlBox");
        const range = document.createRange();
        range.selectNodeContents(box);
        window.getSelection().removeAllRanges();
        window.getSelection().addRange(range);
      });
    }

    // Auto-select URL text on page load for easy manual copy
    window.onload = () => {
      const box = document.getElementById("urlBox");
      const range = document.createRange();
      range.selectNodeContents(box);
      window.getSelection().removeAllRanges();
      window.getSelection().addRange(range);
    };
  </script>
</body>
</html>
""", 200


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Flask thread
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_flask():
    port = int(os.getenv("PORT", 10000))
    LOGGER.info(f"🌐 Flask listening on port {port}")
    flask_app.run(host="0.0.0.0", port=port, use_reloader=False)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Signal handler
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def handle_shutdown_signal(signum, _frame):
    sig_name = signal.Signals(signum).name
    LOGGER.info(f"🛑 Signal {sig_name} received — shutting down...")
    _shutdown.set()
    _bot_running.clear()
    if bot_process and bot_process.poll() is None:
        LOGGER.info("Terminating bot subprocess...")
        bot_process.terminate()
        try:
            bot_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            LOGGER.warning("Bot did not stop in time — killing.")
            bot_process.kill()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Log streamer
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def stream_output(pipe, label: str = "BOT"):
    """Stream subprocess stdout/stderr to our logger so logs appear in Render dashboard."""
    try:
        for line in iter(pipe.readline, b""):
            text = line.decode("utf-8", errors="replace").rstrip()
            if text:
                LOGGER.info(f"[{label}] {text}")
    except Exception:
        pass
    finally:
        pipe.close()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Bot subprocess runner with exponential backoff
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BACKOFF_MIN     = 5    # seconds — first restart delay
BACKOFF_MAX     = 60   # seconds — maximum restart delay
BACKOFF_FACTOR  = 2    # multiply delay on each consecutive crash
BACKOFF_RESET   = 300  # seconds — reset delay if bot ran this long

def run_bot_subprocess():
    global bot_process

    python   = sys.executable
    bot_dir  = os.path.dirname(os.path.abspath(__file__))
    delay    = BACKOFF_MIN

    while not _shutdown.is_set():
        LOGGER.info(f"▶️  Starting bot subprocess (bot.py) — attempt #{_state['restart_count'] + 1}")
        launch_time = time.time()

        try:
            bot_process = subprocess.Popen(
                [python, "-u", "bot.py"],   # -u = unbuffered stdout
                cwd=bot_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,   # merge stderr into stdout
            )
        except Exception as e:
            LOGGER.error(f"❌ Failed to start bot subprocess: {e}. Retrying in {delay}s...")
            _shutdown.wait(timeout=delay)
            delay = min(delay * BACKOFF_FACTOR, BACKOFF_MAX)
            continue

        _state["bot_pid"] = bot_process.pid
        _bot_running.set()
        LOGGER.info(f"✅ Bot subprocess started (PID={bot_process.pid})")

        # Stream logs in background thread
        out_thread = threading.Thread(
            target=stream_output,
            args=(bot_process.stdout, "BOT"),
            daemon=True,
        )
        out_thread.start()

        bot_process.wait()
        out_thread.join(timeout=2)

        _bot_running.clear()
        exit_code              = bot_process.returncode
        _state["last_exit_code"] = exit_code
        _state["restart_count"] += 1
        runtime = time.time() - launch_time

        LOGGER.info(f"Bot subprocess exited (code={exit_code}, runtime={runtime:.0f}s)")

        if _shutdown.is_set():
            LOGGER.info("Shutdown requested — not restarting.")
            break

        # Exponential backoff — reset if bot ran long enough (healthy run)
        if runtime >= BACKOFF_RESET:
            delay = BACKOFF_MIN
            LOGGER.info(f"Bot ran {runtime:.0f}s — resetting restart delay to {delay}s")
        else:
            LOGGER.warning(
                f"⚠️  Bot exited after {runtime:.0f}s (code={exit_code}). "
                f"Restarting in {delay}s... (restart #{_state['restart_count']})"
            )

        _shutdown.wait(timeout=delay)
        delay = min(delay * BACKOFF_FACTOR, BACKOFF_MAX)

    LOGGER.info("Bot runner loop finished.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Entry point
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    # Startup banner
    LOGGER.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    LOGGER.info("  Google Drive Access Manager Bot")
    LOGGER.info(f"  Python  : {platform.python_version()}")
    LOGGER.info(f"  Platform: {platform.system()} {platform.release()}")
    LOGGER.info(f"  PID     : {os.getpid()}")
    LOGGER.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    signal.signal(signal.SIGTERM, handle_shutdown_signal)
    signal.signal(signal.SIGINT,  handle_shutdown_signal)

    # Flask in daemon thread — dies when main thread exits
    LOGGER.info("🌐 Starting Flask thread...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Bot runner in non-daemon thread — keeps process alive
    LOGGER.info("🤖 Starting bot runner thread...")
    bot_thread = threading.Thread(target=run_bot_subprocess, daemon=False)
    bot_thread.start()

    bot_thread.join()
    LOGGER.info("server.py exiting.")
