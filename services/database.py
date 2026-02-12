from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, ADMIN_IDS
import time
import logging

LOGGER = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self._client = None
        self.db = None
        self.admins = None
        self.logs = None
        self.settings = None
        self.states = None
        self.cache = None

    async def init(self):
        """Initialize database connection and verify indices."""
        if not MONGO_URI:
            LOGGER.error("MONGO_URI is not set!")
            return

        self._client = AsyncIOMotorClient(MONGO_URI)
        self.db = self._client.drive_bot
        
        self.admins = self.db.admins
        self.logs = self.db.logs
        self.settings = self.db.settings
        self.states = self.db.states
        self.cache = self.db.cache

        # Bootstrap initial admins from config
        if ADMIN_IDS:
            for admin_id in ADMIN_IDS:
                await self.add_admin(admin_id, "Config Admin")
        
        LOGGER.info("Database initialized successfully.")

    # --- Admin Management ---
    async def is_admin(self, user_id):
        return await self.admins.find_one({"user_id": int(user_id)}) is not None

    async def add_admin(self, user_id, name):
        if not await self.is_admin(user_id):
            await self.admins.insert_one({
                "user_id": int(user_id),
                "name": name,
                "added_at": time.time()
            })
            return True
        return False

    async def remove_admin(self, user_id):
        result = await self.admins.delete_one({"user_id": int(user_id)})
        return result.deleted_count > 0

    async def get_all_admins(self):
        cursor = self.admins.find({})
        return [admin async for admin in cursor]

    # --- Logging ---
    async def log_action(self, admin_id, admin_name, action, details):
        """
        Log an administrative action.
        details: dict containing target_email, folder_name, role, etc.
        """
        log_entry = {
            "admin_id": admin_id,
            "admin_name": admin_name,
            "action": action,
            "details": details,
            "timestamp": time.time()
        }
        await self.logs.insert_one(log_entry)

    async def get_logs(self, limit=50, skip=0):
        # Sort by timestamp descending
        cursor = self.logs.find({}).sort("timestamp", -1).skip(skip).limit(limit)
        total = await self.logs.count_documents({})
        logs = [log async for log in cursor]
        return logs, total

    async def clear_logs(self):
        await self.logs.delete_many({})

    # --- Settings ---
    async def get_setting(self, key, default=None):
        doc = await self.settings.find_one({"key": key})
        return doc["value"] if doc else default

    async def update_setting(self, key, value):
        await self.settings.update_one(
            {"key": key},
            {"$set": {"value": value}},
            upsert=True
        )

    # --- State Management (For Conversation Flow) ---
    async def set_state(self, user_id, state, data=None):
        if data is None:
            data = {}
        await self.states.update_one(
            {"user_id": int(user_id)},
            {"$set": {"state": state, "data": data, "updated_at": time.time()}},
            upsert=True
        )

    async def get_state(self, user_id):
        doc = await self.states.find_one({"user_id": int(user_id)})
        if doc:
            return doc.get("state"), doc.get("data", {})
        return None, {}

    async def delete_state(self, user_id):
        await self.states.delete_one({"user_id": int(user_id)})

    # --- Folder Cache ---
    async def get_cached_folders(self, ttl_minutes=10):
        """Return cached folders if fresh (within TTL), else None."""
        doc = await self.cache.find_one({"key": "folders"})
        if doc:
            age = time.time() - doc.get("cached_at", 0)
            if age < ttl_minutes * 60:
                return doc.get("folders", [])
        return None

    async def set_cached_folders(self, folders):
        """Store folder list with current timestamp."""
        await self.cache.update_one(
            {"key": "folders"},
            {"$set": {"folders": folders, "cached_at": time.time()}},
            upsert=True
        )

    async def clear_folder_cache(self):
        """Invalidate folder cache."""
        await self.cache.delete_one({"key": "folders"})

db = Database()
