# Google Drive Access Manager - Configuration

import os
import re
import time
from dotenv import load_dotenv

load_dotenv()

# Global Start Time
START_TIME = time.time()
VERSION = "2.1.1"

# --- Telegram Credentials ---
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- Database ---
MONGO_URI = os.getenv("MONGO_URI")

# --- Admin ---
# Accept comma and/or whitespace separated IDs (Render envs are often multiline).
def _parse_admin_ids(raw: str) -> set[int]:
    if not raw:
        return set()
    parts = re.split(r"[\s,]+", raw.strip())
    return {int(p) for p in parts if p and p.isdigit()}

ADMIN_IDS = _parse_admin_ids(os.getenv("ADMIN_IDS", "8123066073"))

# --- Logging ---
import logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
LOGGER = logging.getLogger(__name__)
LOGGER.info(f"Loaded {len(ADMIN_IDS)} admin id(s) from ADMIN_IDS env")

# --- Validation ---
if not all([API_ID, API_HASH, BOT_TOKEN, MONGO_URI]):
    LOGGER.warning("Missing required environment variables! Please check .env file.")
