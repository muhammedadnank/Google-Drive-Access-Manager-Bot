# Google Drive Access Manager - Configuration

import os
import time
from dotenv import load_dotenv

load_dotenv()

# Global Start Time
START_TIME = time.time()
VERSION = "2.1.0"

# --- Telegram Credentials ---
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- Database ---
MONGO_URI = os.getenv("MONGO_URI")

# --- Admin ---
# Store as a set of integers for efficiency
ADMIN_IDS = set(map(int, os.getenv("ADMIN_IDS", "").split(','))) if os.getenv("ADMIN_IDS") else set()

# --- Logging ---
import logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
LOGGER = logging.getLogger(__name__)

# --- Validation ---
if not all([API_ID, API_HASH, BOT_TOKEN, MONGO_URI]):
    LOGGER.warning("Missing required environment variables! Please check .env file.")
