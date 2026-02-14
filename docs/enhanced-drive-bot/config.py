"""
Configuration Management
VJ-FILTER-BOT inspired centralized config
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Bot configuration (VJ-style centralized)"""
    
    # ═══════════════════════════════════════
    # TELEGRAM CREDENTIALS
    # ═══════════════════════════════════════
    API_ID = int(os.environ.get("API_ID", "0"))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    
    # ═══════════════════════════════════════
    # ADMIN CONFIGURATION
    # ═══════════════════════════════════════
    ADMIN_IDS = [
        int(admin_id.strip()) 
        for admin_id in os.environ.get("ADMIN_IDS", "").split(",")
        if admin_id.strip()
    ]
    
    # First admin is super admin
    SUPER_ADMIN_ID = ADMIN_IDS[0] if ADMIN_IDS else None
    
    # ═══════════════════════════════════════
    # DATABASE CONFIGURATION
    # ═══════════════════════════════════════
    MONGO_URI = os.environ.get("MONGO_URI", "")
    DB_NAME = os.environ.get("DB_NAME", "drive_access_bot")
    
    # Collections
    COLLECTION_ADMINS = "admins"
    COLLECTION_LOGS = "logs"
    COLLECTION_SETTINGS = "settings"
    COLLECTION_STATES = "states"
    COLLECTION_CACHE = "cache"
    COLLECTION_GRANTS = "grants"
    COLLECTION_BROADCASTS = "broadcasts"
    
    # ═══════════════════════════════════════
    # GOOGLE DRIVE CONFIGURATION
    # ═══════════════════════════════════════
    CREDENTIALS_FILE = "credentials.json"
    TOKEN_FILE = "token.json"
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    # Cache settings
    CACHE_TTL = int(os.environ.get("CACHE_TTL", "3600"))  # 1 hour
    CACHE_ENABLED = os.environ.get("CACHE_ENABLED", "true").lower() == "true"
    
    # ═══════════════════════════════════════
    # CHANNEL CONFIGURATION
    # ═══════════════════════════════════════
    CHANNEL_ID = os.environ.get("CHANNEL_ID", "")
    CHANNEL_ENABLED = os.environ.get("CHANNEL_ENABLED", "false").lower() == "true"
    
    # ═══════════════════════════════════════
    # BOT SETTINGS (VJ-inspired)
    # ═══════════════════════════════════════
    
    # Default access settings
    DEFAULT_ROLE = os.environ.get("DEFAULT_ROLE", "reader")
    DEFAULT_EXPIRY_DAYS = int(os.environ.get("DEFAULT_EXPIRY_DAYS", "30"))
    
    # Pagination
    DEFAULT_PAGE_SIZE = int(os.environ.get("DEFAULT_PAGE_SIZE", "5"))
    MIN_PAGE_SIZE = 3
    MAX_PAGE_SIZE = 10
    
    # Notifications
    AUTO_EXPIRE_NOTIFICATIONS = os.environ.get(
        "AUTO_EXPIRE_NOTIFICATIONS", "true"
    ).lower() == "true"
    
    GRANT_NOTIFICATIONS = os.environ.get(
        "GRANT_NOTIFICATIONS", "true"
    ).lower() == "true"
    
    REVOKE_NOTIFICATIONS = os.environ.get(
        "REVOKE_NOTIFICATIONS", "true"
    ).lower() == "true"
    
    # Broadcast settings
    BROADCAST_DELAY = float(os.environ.get("BROADCAST_DELAY", "0.5"))
    MAX_BROADCAST_BATCH = int(os.environ.get("MAX_BROADCAST_BATCH", "100"))
    
    # ═══════════════════════════════════════
    # FEATURE TOGGLES (VJ-style)
    # ═══════════════════════════════════════
    ENABLE_AUTO_EXPIRE = os.environ.get("ENABLE_AUTO_EXPIRE", "true").lower() == "true"
    ENABLE_BULK_IMPORT = os.environ.get("ENABLE_BULK_IMPORT", "true").lower() == "true"
    ENABLE_ANALYTICS = os.environ.get("ENABLE_ANALYTICS", "true").lower() == "true"
    ENABLE_BROADCAST = os.environ.get("ENABLE_BROADCAST", "true").lower() == "true"
    
    # ═══════════════════════════════════════
    # RATE LIMITING
    # ═══════════════════════════════════════
    RATE_LIMIT_ENABLED = os.environ.get("RATE_LIMIT_ENABLED", "true").lower() == "true"
    MAX_REQUESTS_PER_MINUTE = int(os.environ.get("MAX_REQUESTS_PER_MINUTE", "10"))
    
    # ═══════════════════════════════════════
    # LOGGING
    # ═══════════════════════════════════════
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # ═══════════════════════════════════════
    # BOT INFO
    # ═══════════════════════════════════════
    BOT_NAME = "Drive Access Manager"
    BOT_VERSION = "3.0.0"
    BOT_DESCRIPTION = "Enhanced with VJ-FILTER-BOT patterns"
    
    # ═══════════════════════════════════════
    # VALIDATION
    # ═══════════════════════════════════════
    @classmethod
    def validate(cls) -> tuple[bool, list]:
        """Validate configuration (VJ pattern)"""
        errors = []
        
        if not cls.API_ID or cls.API_ID == 0:
            errors.append("API_ID is not set")
        
        if not cls.API_HASH:
            errors.append("API_HASH is not set")
        
        if not cls.BOT_TOKEN:
            errors.append("BOT_TOKEN is not set")
        
        if not cls.MONGO_URI:
            errors.append("MONGO_URI is not set")
        
        if not cls.ADMIN_IDS:
            errors.append("ADMIN_IDS is not set")
        
        if not os.path.exists(cls.CREDENTIALS_FILE):
            errors.append(f"{cls.CREDENTIALS_FILE} not found")
        
        return len(errors) == 0, errors
    
    @classmethod
    def print_config(cls):
        """Print configuration summary"""
        print(f"""
╔════════════════════════════════════════════╗
║  ⚙️  Configuration Summary                 ║
╠════════════════════════════════════════════╣
║  Bot Name    : {cls.BOT_NAME:<28} ║
║  Version     : {cls.BOT_VERSION:<28} ║
║  Database    : {cls.DB_NAME:<28} ║
║  Admins      : {len(cls.ADMIN_IDS):<28} ║
║  Channel     : {'Enabled' if cls.CHANNEL_ENABLED else 'Disabled':<28} ║
║  Auto-Expire : {'Enabled' if cls.ENABLE_AUTO_EXPIRE else 'Disabled':<28} ║
║  Broadcast   : {'Enabled' if cls.ENABLE_BROADCAST else 'Disabled':<28} ║
╚════════════════════════════════════════════╝
        """)

# Validate config on import
is_valid, errors = Config.validate()
if not is_valid:
    print("❌ Configuration errors:")
    for error in errors:
        print(f"  • {error}")
    exit(1)
